#!/usr/bin/env python3
"""Run the fixed 36-candidate four-slot product without emitting candidates."""
from __future__ import annotations

import argparse
import os
import sys
from itertools import product
from pathlib import Path

from oracle import (
    CIPHERTEXT_B64,
    ESCROW,
    PZL8_ADDRESS,
    PZL8_ANSWER,
    PZL8_CIPHERTEXT_B64,
    check,
    decode_wallet,
)

# Candidate values remain local to this runner. Output intentionally never includes one.
SLOT_1 = ("weve", "a16z", "anno")
SLOT_5 = ("e4d5", "1984")
SLOT_7 = ("pull", "vest", "pool")
SLOT_8 = ("base", "dots")
FIXED = ("md12", "a384", "cash", "root")
COVERAGE_INDEX = {"head": 0, "middle": 17, "tail": 35}
SECRET_PATH = Path.home() / ".secrets" / "open-crypto-puzzles" / "arweave-puzzle-3-match.json"


def candidates():
    for slot_1, slot_5, slot_7, slot_8 in product(SLOT_1, SLOT_5, SLOT_7, SLOT_8):
        yield "".join((slot_1, FIXED[0], FIXED[1], FIXED[2], slot_5, FIXED[3], slot_7, slot_8))


def check_index(index: int) -> bool:
    for current, candidate in enumerate(candidates()):
        if current == index:
            matched, address = check(candidate)
            return matched and address == ESCROW
    raise ValueError("coverage index outside fixed product")


def positive_control() -> bool:
    matched, address = check(PZL8_ANSWER, PZL8_CIPHERTEXT_B64, lowercase_input=False)
    return matched and address == PZL8_ADDRESS


def store_match(candidate: str) -> None:
    plaintext = decode_wallet(CIPHERTEXT_B64, candidate)
    SECRET_PATH.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(SECRET_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, "w", encoding="latin-1") as secret_file:
        secret_file.write(plaintext)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage", choices=COVERAGE_INDEX)
    parser.add_argument("--positive-control", action="store_true")
    args = parser.parse_args()

    if args.positive_control:
        matched = positive_control()
        print(f"POSITIVE CONTROL: {'MATCH' if matched else 'FAILED'}")
        return 0 if matched else 1

    if args.coverage:
        matched = check_index(COVERAGE_INDEX[args.coverage])
        print(f"COVERAGE {args.coverage}: {'MATCH' if matched else 'NO MATCH'}")
        return 0 if matched else 1

    for candidate in candidates():
        matched, address = check(candidate)
        if matched and address == ESCROW:
            store_match(candidate)
            print(f"MATCH: secure local artifact written to {SECRET_PATH}")
            return 0
    print("PRODUCT COMPLETE: 0 MATCH")
    return 1


if __name__ == "__main__":
    sys.exit(main())
