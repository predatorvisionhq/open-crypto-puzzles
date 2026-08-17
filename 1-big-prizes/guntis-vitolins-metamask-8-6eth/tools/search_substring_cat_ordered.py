#!/usr/bin/env python3
"""Run the conservative ``cat``-inside-``cattle`` substring branch.

The author explicitly allowed a list word inside a longer written word.  This
solver tests only the strongest literal instance: the BIP39 word ``cat`` as
the contiguous prefix of the planted word ``cattle``.  It substitutes that
term at cattle's source-order slot; it does not enumerate arbitrary substrings.
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import os
import subprocess
import sys
import time
from pathlib import Path

from bip_utils import Bip39MnemonicValidator, Bip39Languages
from bip_utils.bip.bip39.bip39_mnemonic_utils import Bip39WordsListGetter

ROOT = Path(__file__).resolve().parents[1]
ORACLE_PATH = ROOT / "tools" / "oracle.py"
MAX_SECONDS = 2 * 60 * 60

# ``cat`` substitutes for the exact planted host ``cattle``; all other post
# terms retain the narrow post-first/source-order reading used in L1a.
POST_SKELETON = ("dutch", "cat", "forest", "wood", "fiber", "fork")
WATER_WORDS = ("fog", "cloud")
VIDEO_CONTENT = ("expect", "easy", "dark", "lake", "think", "sing", "song", "goat")


def load_oracle():
    spec = importlib.util.spec_from_file_location("guntis_oracle", ORACLE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load certified oracle")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_family() -> list[str]:
    """Generate all source-order video completions of the cat substitution."""
    family: list[str] = []
    for selected in itertools.combinations(VIDEO_CONTENT, 4):
        for water_word in WATER_WORDS:
            words = (
                POST_SKELETON[:4]
                + (water_word,)
                + POST_SKELETON[4:]
                + selected
                + ("parrot",)
            )
            if len(words) != 12:
                raise AssertionError("family construction produced a non-12-word input")
            family.append(" ".join(words))

    expected = len(WATER_WORDS) * 70  # C(8, 4)
    if len(family) != expected or len(set(family)) != expected:
        raise AssertionError("family cardinality or uniqueness invariant failed")
    return family


def benchmark_inputs() -> list[str]:
    """Return the public, checksum-valid vectors used by oracle.py self-test."""
    words = Bip39WordsListGetter().GetByLanguage(Bip39Languages.ENGLISH)
    validator = Bip39MnemonicValidator()
    base = ["abandon"] * 11
    vectors = [
        " ".join(base + [words.GetWordAtIdx(index)])
        for index in range(words.Length())
        if validator.IsValid(" ".join(base + [words.GetWordAtIdx(index)]))
    ]
    if len(vectors) != 128:
        raise AssertionError("canonical benchmark set no longer has 128 valid inputs")
    return vectors


def run_oracle_batch(candidates: list[str]) -> tuple[list[str], float]:
    started = time.monotonic()
    result = subprocess.run(
        [sys.executable, str(ORACLE_PATH), "--stdin"],
        input="\n".join(candidates) + "\n",
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    elapsed = time.monotonic() - started
    if result.returncode not in (0, 1):
        raise RuntimeError(f"oracle execution failed: {result.stderr.strip()}")
    verdicts = result.stdout.splitlines()
    if len(verdicts) != len(candidates):
        raise RuntimeError("oracle output cardinality does not match submitted candidates")
    return verdicts, elapsed


def check_witness(oracle) -> None:
    """Verify a known public positive through the oracle's MATCH branch."""
    if oracle.derive_address(oracle.VECTOR_MNEMONIC) != oracle.VECTOR_ADDRESS:
        raise RuntimeError("canonical BIP39 witness failed address derivation")
    if oracle.attempt(oracle.VECTOR_MNEMONIC)[0] != "NO MATCH":
        raise RuntimeError("canonical witness did not traverse live comparison")

    live_target = oracle.TARGET_ADDRESS
    try:
        oracle.TARGET_ADDRESS = oracle.VECTOR_ADDRESS
        witness_verdict, _ = oracle.attempt(oracle.VECTOR_MNEMONIC)
    finally:
        oracle.TARGET_ADDRESS = live_target
    if witness_verdict != "MATCH":
        raise RuntimeError("canonical witness failed the exact oracle MATCH branch")
    print("WITNESS canonical public BIP39 exact-MATCH path: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="benchmark then execute the family")
    args = parser.parse_args()
    if not args.run:
        parser.error("use --run")

    oracle = load_oracle()
    check_witness(oracle)

    benchmark = benchmark_inputs()
    print(f"BENCHMARK PLAN N={len(benchmark)} valid derivations through oracle.py --stdin")
    benchmark_verdicts, benchmark_seconds = run_oracle_batch(benchmark)
    if any(verdict != "NO MATCH" for verdict in benchmark_verdicts):
        raise RuntimeError("benchmark did not return expected live-target NO MATCH verdicts")
    rate = len(benchmark) / benchmark_seconds
    print(f"BENCHMARK RESULT N={len(benchmark)} D={rate:.2f} derivations/s")

    family = build_family()
    validator = Bip39MnemonicValidator()
    valid_family = [candidate for candidate in family if validator.IsValid(candidate)]
    estimate = len(valid_family) / rate
    print(
        "FAMILY PLAN "
        f"enumerated={len(family)} checksum-valid N={len(valid_family)} "
        f"D={rate:.2f} derivations/s t={estimate:.3f}s (limit={MAX_SECONDS}s)"
    )
    if estimate > MAX_SECONDS:
        raise RuntimeError("family exceeds the two-hour execution limit")

    verdicts, elapsed = run_oracle_batch(valid_family)
    matches = [index for index, verdict in enumerate(verdicts) if verdict == "MATCH"]
    if any(verdict not in {"NO MATCH", "MATCH"} for verdict in verdicts):
        raise RuntimeError("oracle returned an unexpected valid-input verdict")
    actual_rate = len(valid_family) / elapsed if elapsed else float("inf")
    if matches:
        secrets = Path.home() / ".secrets" / "open-crypto-puzzles"
        secrets.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(secrets, 0o700)
        secret_path = secrets / "guntis-vitolins-metamask-8-6eth-match.txt"
        descriptor = os.open(secret_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as secret:
            secret.write(valid_family[matches[0]] + "\n")
        print(f"MATCH STORED {secret_path}")
        return 0

    print(
        "FAMILY RESULT "
        f"enumerated={len(family)} derived={len(valid_family)} "
        f"D={actual_rate:.2f} derivations/s result=0 MATCH"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
