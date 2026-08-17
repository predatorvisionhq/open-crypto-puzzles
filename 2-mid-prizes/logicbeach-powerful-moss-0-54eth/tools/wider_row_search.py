#!/usr/bin/env python3
"""Bounded +/-2-row search for the Powerful Moss clock-wordlist hypothesis."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import stat
import time
from pathlib import Path

from bip_utils.bip.bip39.bip39_mnemonic import Bip39Languages
from bip_utils.bip.bip39.bip39_mnemonic_utils import Bip39WordsListGetter

import oracle

WIDTHS = range(169, 176)
UNCERTAIN_HOURS = (1, 2, 3, 5, 6, 7, 9, 10, 11)
ORDERS = (
    tuple(range(1, 13)),
    tuple(range(12, 0, -1)),
    (12, *range(1, 12)),
    (12, *range(11, 0, -1)),
)
WITNESS_MNEMONIC = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
WITNESS_ADDRESS = "0x9858effd232b4033e47d90003d41ec34ecaeda94"


def load_words() -> list[str]:
    words = Bip39WordsListGetter().GetByLanguage(Bip39Languages.ENGLISH)
    return [words.GetWordAtIdx(i) for i in range(words.Length())]


def wrap(words: list[str], width: int) -> tuple[dict[str, tuple[int, int]], list[list[str]]]:
    locations: dict[str, tuple[int, int]] = {}
    rows: list[list[str]] = []
    row: list[str] = []
    column = 0
    for word in words:
        needed = len(word) + (1 if row else 0)
        if row and column + needed > width:
            rows.append(row)
            row = []
            column = 0
        if row:
            column += 1
        locations[word] = (len(rows), column)
        row.append(word)
        column += len(word)
    rows.append(row)
    return locations, rows


def word_at(rows: list[list[str]], row_index: int, column: int) -> str | None:
    if row_index < 0 or row_index >= len(rows):
        return None
    cursor = 0
    for word in rows[row_index]:
        if cursor <= column < cursor + len(word):
            return word
        cursor += len(word) + 1
    return None


def derive_extras(base: dict[int, list[str]], words: list[str]) -> dict[int, list[str]]:
    extras = {hour: set() for hour in UNCERTAIN_HOURS}
    for width in WIDTHS:
        locations, rows = wrap(words, width)
        for hour in UNCERTAIN_HOURS:
            group = base[hour]
            spans = [
                (locations[word][1], locations[word][1] + len(word), locations[word][0])
                for word in group
            ]
            low = max(start for start, _, _ in spans)
            high = min(end for _, end, _ in spans)
            if low < high:
                columns = range(low, high)
            else:
                average = round(sum((start + end - 1) / 2 for start, end, _ in spans) / len(spans))
                columns = range(max(0, average - 2), average + 3)
            center_row = spans[1][2]
            for row_delta in (-2, 2):
                for column in columns:
                    word = word_at(rows, center_row + row_delta, column)
                    if word is not None and word not in group:
                        extras[hour].add(word)
    return {hour: sorted(values) for hour, values in extras.items()}


def load_base(folder: Path) -> dict[int, list[str]]:
    data = json.loads((folder / "data" / "seed-grid.json").read_text())
    return {entry["hour"]: entry["candidates"] for entry in data["hours"]}


def candidate_count(base: dict[int, list[str]], extras: dict[int, list[str]]) -> int:
    per_hour = (
        len(extras[opened_hour])
        * math.prod(len(base[hour]) for hour in UNCERTAIN_HOURS if hour != opened_hour)
        for opened_hour in UNCERTAIN_HOURS
    )
    return len(ORDERS) * sum(per_hour)


def candidates(base: dict[int, list[str]], extras: dict[int, list[str]]):
    for opened_hour in UNCERTAIN_HOURS:
        other_hours = [hour for hour in UNCERTAIN_HOURS if hour != opened_hour]
        pools = [base[hour] for hour in other_hours]
        for extra in extras[opened_hour]:
            for choices in itertools.product(*pools):
                by_hour = {hour: base[hour][0] for hour in range(1, 13)}
                by_hour[opened_hour] = extra
                by_hour.update(zip(other_hours, choices))
                for order in ORDERS:
                    yield " ".join(by_hour[hour] for hour in order)


def save_match(path: Path, mnemonic: str) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as handle:
        handle.write(mnemonic + "\n")
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)

def check_candidate(mnemonic: str, target: str | None = None):
    """Route target candidates and known-good witnesses through one oracle call site."""
    return oracle.check(mnemonic, target) if target is not None else oracle.check(mnemonic)




def run(
    limit: int | None,
    skip: int,
    match_path: Path,
    benchmark_only: bool,
    coverage_only: bool,
) -> int:
    folder = Path(__file__).resolve().parent.parent
    base = load_base(folder)
    extras = derive_extras(base, load_words())
    total = candidate_count(base, extras)
    if skip < 0 or skip > total:
        raise ValueError("skip is outside the candidate space")

    planned = total - skip
    if limit is not None:
        planned = min(planned, limit)
    witness_positions = {0, planned // 2, planned - 1} if planned else set()
    witness_hits = 0
    print(f"N={total} skip={skip} planned={planned}")

    started = time.monotonic()
    tested = 0
    checksum_valid = 0
    stream_hash = hashlib.sha256()
    iterator = itertools.islice(candidates(base, extras), skip, skip + planned)
    for index, mnemonic in enumerate(iterator):
        if index in witness_positions:
            if check_candidate(WITNESS_MNEMONIC, WITNESS_ADDRESS) is None:
                raise RuntimeError("known-good witness failed through the candidate check path")
            witness_hits += 1
        tested += 1
        stream_hash.update(hashlib.sha256(mnemonic.encode()).digest())
        if coverage_only:
            continue
        hit = check_candidate(mnemonic)
        if hit is not None:
            save_match(match_path, mnemonic)
            print(f"MATCH held locally at {match_path}; stop without broadcasting")
            return 0
        # The oracle rejects invalid checksums before derivation. Count validity separately.
        if oracle.Bip39MnemonicValidator().IsValid(mnemonic):
            checksum_valid += 1

    if coverage_only:
        elapsed = time.monotonic() - started
        print(
            f"COVERAGE_OK tested={tested} witness_hits={witness_hits} elapsed={elapsed:.3f}s "
            f"stream_commitment={stream_hash.hexdigest()}"
        )
        return 0
    elapsed = time.monotonic() - started
    rate = tested / elapsed if elapsed else 0.0
    remaining = total - skip - tested
    eta = remaining / rate if rate else float("inf")
    print(
        f"NO_MATCH tested={tested} checksum_valid={checksum_valid} witness_hits={witness_hits} "
        f"elapsed={elapsed:.3f}s D={rate:.2f}_raw_per_s remaining={remaining} t={eta:.3f}s "
        f"stream_commitment={stream_hash.hexdigest()}"
    )
    if benchmark_only:
        return 0
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--skip", type=int, default=0)
    parser.add_argument("--benchmark-only", action="store_true")
    parser.add_argument("--coverage-only", action="store_true")
    parser.add_argument("--match-path", type=Path, required=True)
    args = parser.parse_args()
    return run(args.limit, args.skip, args.match_path, args.benchmark_only, args.coverage_only)


if __name__ == "__main__":
    raise SystemExit(main())
