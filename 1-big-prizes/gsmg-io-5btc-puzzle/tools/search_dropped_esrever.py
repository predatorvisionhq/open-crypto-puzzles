#!/usr/bin/env python3
"""Bounded, exact-address checks for GSMG's dropped-letter and esrever leads.

The repository pins a 570-character ciphertext manually extracted from the
public SalPhaseIon transformation. The full upstream token stream is not
shipped here, so the reported 90-token/104-token/``z`` boundaries are not
self-contained. No candidate strings are printed. A hit is written once with
mode 0600.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path

from oracle import BLOB_B64, attempt

BIFID_KEY = "DBIFHCEG"
BIFID_CIPHERTEXT = "FAEDGGEEDFCBDABHHGGCADCFEDDGFDGBGIGAAEDGGIAFAECGHGGCDAIHEHAHBAHIGCEIFGBFGEFGAIFABIFAGAEGEACGBBEAGFGGEEGGAFBACGFCDBEIFFAAFCIDAHGDEEFGHHCGGAEGDEBHHEGEGHCEGADFBDIAGEFCICGGIFDCGAAGGFBIGAICFBHECAECBCEIAICEBGBGIECDEGGFGEGAEDGGFIICIIIFIFHGGCGFGDCDGGEFCBEEIGEFIBGIBGGGHHFBCGIFDEHEDFDAGICDBHICGAIEDAEHAHGHHCIHDGHFHBIICECBIICHIHIIIGIDDGEHHDFDCHCBAFGFBHAHEAGEGECAFEHGCFGGGGCAGFHHGHBAIHIDIEHHFDEGGDGCIHGGGGGHADAHIGIGBGECGEDFCDGGACCDEHIICIGFBFFHGGAEIDBBEIBBEIIFDGFDHIEEEIEEECIFDGDAHDIGGFHEGFIAFFIGGBCBCEHCEABFBEDBIIBFBFDEDEEHGIGFAAIGGAGBEIICHIEDIFBEHGBCCAHHBIIBIBBIBDCBAHAIDHFAHIIHIC"


def keyed_square(key: str) -> str:
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    chars: list[str] = []
    for char in key + alphabet:
        if char not in chars and char in alphabet:
            chars.append(char)
    assert len(chars) == 25
    return "".join(chars)


def bifid_decrypt(ciphertext: str, key: str) -> str:
    square = keyed_square(key)
    positions = {char: divmod(index, 5) for index, char in enumerate(square)}
    coordinates = [coordinate for char in ciphertext for coordinate in positions[char]]
    size = len(ciphertext)
    return "".join(square[coordinates[index] * 5 + coordinates[size + index]] for index in range(size))


def bifid_encrypt(plaintext: str, key: str) -> str:
    square = keyed_square(key)
    positions = {char: divmod(index, 5) for index, char in enumerate(square)}
    rows = [positions[char][0] for char in plaintext]
    columns = [positions[char][1] for char in plaintext]
    coordinates = rows + columns
    return "".join(square[coordinates[index] * 5 + coordinates[index + 1]] for index in range(0, len(coordinates), 2))


def store_match(candidate: str) -> None:
    secret_dir = Path.home() / ".secrets" / "open-crypto-puzzles"
    secret_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    target = secret_dir / "gsmg-io-5btc-puzzle-match.txt"
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as output:
        output.write(candidate)


def check_family(candidates: list[str]) -> tuple[int, int]:
    unique = list(dict.fromkeys(candidates))
    for index, candidate in enumerate(unique, start=1):
        matched, _ = attempt(candidate)
        if matched:
            store_match(candidate)
            return index, 1
    return len(unique), 0


def main() -> int:
    plaintext = bifid_decrypt(BIFID_CIPHERTEXT, BIFID_KEY)
    assert plaintext.startswith("BTCSEED")
    assert bifid_encrypt(plaintext, BIFID_KEY) == BIFID_CIPHERTEXT

    relevant_interleave = plaintext[1::2]
    reduced = "".join(char for char in relevant_interleave if char not in "IO")
    dropped = "".join(char for char in relevant_interleave if char in "IO")
    assert len(plaintext) == 570
    assert len(relevant_interleave) == 285
    assert len(reduced) == 256 and len(set(reduced)) == 23
    assert len(dropped) == 29

    reversed_dropped = dropped[::-1]
    dropped_family = [
        dropped,
        reversed_dropped,
        bifid_encrypt(dropped, BIFID_KEY),
        bifid_decrypt(dropped, BIFID_KEY),
        bifid_encrypt(reversed_dropped, BIFID_KEY),
        bifid_decrypt(reversed_dropped, BIFID_KEY),
    ]
    esrever_family = [
        reduced[::-1],
        reduced[::-1].lower(),
        relevant_interleave[::-1],
        relevant_interleave[::-1].lower(),
        BLOB_B64[::-1],
        base64.b64encode(base64.b64decode(BLOB_B64)[::-1]).decode("ascii"),
    ]
    dropped_tested, dropped_matches = check_family(dropped_family)
    if dropped_matches:
        print(json.dumps({"family": "dropped", "tested": dropped_tested, "matches": 1}))
        return 0
    esrever_tested, esrever_matches = check_family(esrever_family)
    print(json.dumps({
        "reconstruction": {
            "ciphertext_length": len(BIFID_CIPHERTEXT),
            "round_trip": True,
            "plaintext_prefix": plaintext[:7],
            "interleave_length": len(relevant_interleave),
            "dropped_length": len(dropped),
            "reduced_length": len(reduced),
            "reduced_alphabet": len(set(reduced)),
            "dropped_sha256": hashlib.sha256(dropped.encode("ascii")).hexdigest(),
        },
        "families": {"dropped": dropped_tested, "esrever": esrever_tested},
        "matches": dropped_matches + esrever_matches,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
