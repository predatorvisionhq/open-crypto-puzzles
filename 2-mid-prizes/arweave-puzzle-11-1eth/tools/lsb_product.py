#!/usr/bin/env python3
"""Bounded direct-key scan of the two raster-channel LSB streams for Puzzle #11.

The product deliberately stays narrow: channel {L, A}, raster direction {forward,
reverse}, and byte bit significance {MSB-first, LSB-first}. Each scan starts at the
canonical first carrier (top-left for forward, bottom-right for reverse), then treats
consecutive 256 carrier bits as one raw secp256k1 key and uses the exact normalized
Ethereum-address oracle. It does not print candidate keys.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
import time
from collections.abc import Iterator
from pathlib import Path

from coincurve import PrivateKey
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = ROOT / "clues" / "arweave-puzzle-11.png"
EXPECTED_SHA256 = "c6ba4b50fd75181a325f28b620438f740120925a07a23b889dda597546db87e1"
TARGET_ADDRESS = "0xff2142e98e09b5344994f9beb9c56c95506b9f17"
SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
SECRET_PATH = Path.home() / ".secrets" / "open-crypto-puzzles" / "arweave-puzzle-11-1eth.txt"

_MASK64 = (1 << 64) - 1
_ROTATION = (
    (0, 36, 3, 41, 18),
    (1, 44, 10, 45, 2),
    (62, 6, 43, 15, 61),
    (28, 55, 25, 21, 56),
    (27, 20, 39, 8, 14),
)
_ROUND_CONSTANTS = (
    0x0000000000000001,
    0x0000000000008082,
    0x800000000000808A,
    0x8000000080008000,
    0x000000000000808B,
    0x0000000080000001,
    0x8000000080008081,
    0x8000000000008009,
    0x000000000000008A,
    0x0000000000000088,
    0x0000000080008009,
    0x000000008000000A,
    0x000000008000808B,
    0x800000000000008B,
    0x8000000000008089,
    0x8000000000008003,
    0x8000000000008002,
    0x8000000000000080,
    0x000000000000800A,
    0x800000008000000A,
    0x8000000080008081,
    0x8000000000008080,
    0x0000000080000001,
    0x8000000080008008,
)


def _rotl64(value: int, shift: int) -> int:
    return ((value << shift) | (value >> (64 - shift))) & _MASK64 if shift else value


def _keccak_f(state: list[int]) -> None:
    for round_constant in _ROUND_CONSTANTS:
        column = [state[x] ^ state[x + 5] ^ state[x + 10] ^ state[x + 15] ^ state[x + 20] for x in range(5)]
        delta = [column[(x - 1) % 5] ^ _rotl64(column[(x + 1) % 5], 1) for x in range(5)]
        for x in range(5):
            for y in range(5):
                state[x + 5 * y] ^= delta[x]

        rotated = [0] * 25
        for x in range(5):
            for y in range(5):
                rotated[y + 5 * ((2 * x + 3 * y) % 5)] = _rotl64(state[x + 5 * y], _ROTATION[x][y])

        for x in range(5):
            for y in range(5):
                state[x + 5 * y] = rotated[x + 5 * y] ^ ((~rotated[(x + 1) % 5 + 5 * y]) & rotated[(x + 2) % 5 + 5 * y])
                state[x + 5 * y] &= _MASK64
        state[0] ^= round_constant


def keccak_256(message: bytes) -> bytes:
    """Ethereum Keccak-256 (legacy Keccak padding 0x01, not SHA3-256)."""
    rate = 136
    padded = bytearray(message)
    padded.append(0x01)
    padded.extend(b"\0" * ((rate - len(padded) % rate - 1) % rate))
    padded.append(0x80)
    state = [0] * 25
    for offset in range(0, len(padded), rate):
        block = padded[offset : offset + rate]
        for lane in range(rate // 8):
            state[lane] ^= int.from_bytes(block[lane * 8 : lane * 8 + 8], "little")
        _keccak_f(state)
    return b"".join(lane.to_bytes(8, "little") for lane in state)[:32]


def address_for_private_key(candidate: bytes) -> str | None:
    """Return the normalized Ethereum address, or None for an invalid scalar."""
    scalar = int.from_bytes(candidate, "big")
    if not 0 < scalar < SECP256K1_ORDER:
        return None
    encoded = PrivateKey(candidate).public_key.format(compressed=False)[1:]
    return "0x" + keccak_256(encoded)[-20:].hex()


def oracle_match(candidate: bytes) -> bool:
    address = address_for_private_key(candidate)
    return address is not None and address.lower() == TARGET_ADDRESS


BIT_REVERSE_TABLE = bytes(int(f"{value:08b}"[::-1], 2) for value in range(256))


def _pack_msb_stream(bits: bytes) -> bytes:
    """Pack a stream of zero/one carrier values with the first bit as each byte's MSB."""
    end = len(bits) - len(bits) % 8
    return bytes(
        (bits[index] << 7)
        | (bits[index + 1] << 6)
        | (bits[index + 2] << 5)
        | (bits[index + 3] << 4)
        | (bits[index + 4] << 3)
        | (bits[index + 5] << 2)
        | (bits[index + 6] << 1)
        | bits[index + 7]
        for index in range(0, end, 8)
    )




def channel_bits() -> dict[str, bytes]:
    with Image.open(IMAGE_PATH) as image:
        if image.size != (1600, 1105):
            raise ValueError(f"unexpected image size: {image.size}")
        pixels = image.convert("LA").get_flattened_data()
        luminosity = bytearray()
        alpha = bytearray()
        for luma, opacity in pixels:
            luminosity.append(luma & 1)
            alpha.append(opacity & 1)
    return {"L": bytes(luminosity), "A": bytes(alpha)}


def candidate_count(pixel_count: int) -> int:
    return 2 * 2 * 2 * (pixel_count // 256)


def candidates() -> Iterator[bytes]:
    for bit_stream in channel_bits().values():
        for reverse in (False, True):
            msb_stream = _pack_msb_stream(bit_stream[::-1] if reverse else bit_stream)
            for lsb_first in (False, True):
                stream = msb_stream.translate(BIT_REVERSE_TABLE) if lsb_first else msb_stream
                for start in range(0, len(stream) - 31, 32):
                    yield stream[start : start + 32]


def save_match(candidate: bytes) -> Path:
    SECRET_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(SECRET_PATH.parent, 0o700)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(SECRET_PATH, flags, 0o600)
    with os.fdopen(descriptor, "w", encoding="ascii") as secret:
        secret.write(candidate.hex() + "\n")
    if stat.S_IMODE(SECRET_PATH.stat().st_mode) != 0o600:
        raise RuntimeError("secret file permissions are not 0600")
    return SECRET_PATH


def selftest() -> int:
    if keccak_256(b"").hex() != "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470":
        print("SELFTEST FAIL keccak")
        return 1
    if address_for_private_key((1).to_bytes(32, "big")) != "0x7e5f4552091a69125d5dfcb7b8c2659029395bdf":
        print("SELFTEST FAIL ethereum-address")
        return 1
    if address_for_private_key(b"\0" * 32) is not None:
        print("SELFTEST FAIL scalar-validation")
        return 1
    print("SELFTEST OK")
    return 0


def benchmark(rounds: int) -> int:
    count = candidate_count(1600 * 1105)
    witness = next(
        candidate
        for candidate in candidates()
        if 0 < int.from_bytes(candidate, "big") < SECP256K1_ORDER
    )
    started = time.perf_counter()
    for _ in range(rounds):
        oracle_match(witness)
    elapsed = time.perf_counter() - started
    rate = rounds / elapsed
    estimate = count / rate
    print(f"N={count} D={rate:.1f}/s t={estimate:.1f}s ({estimate / 3600:.4f}h) rounds={rounds}")
    return 0 if estimate <= 2 * 3600 else 2


def run() -> int:
    actual_hash = hashlib.sha256(IMAGE_PATH.read_bytes()).hexdigest()
    if actual_hash != EXPECTED_SHA256:
        raise ValueError("image sha256 does not match the published artifact")
    count = candidate_count(1600 * 1105)
    checked = 0
    invalid = 0
    for candidate in candidates():
        checked += 1
        address = address_for_private_key(candidate)
        if address is None:
            invalid += 1
            continue
        if address.lower() == TARGET_ADDRESS:
            print(f"MATCH_SAVED {save_match(candidate)}")
            return 0
    print(f"NO_MATCH scanned={checked} invalid_scalars={invalid} valid_oracle_calls={checked - invalid}")
    if checked != count:
        raise RuntimeError(f"candidate accounting mismatch: expected {count}, saw {checked}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--rounds", type=int, default=200)
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    if sum((args.selftest, args.benchmark, args.run)) != 1:
        parser.error("choose exactly one of --selftest, --benchmark, or --run")
    if args.selftest:
        return selftest()
    if args.benchmark:
        return benchmark(args.rounds)
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
