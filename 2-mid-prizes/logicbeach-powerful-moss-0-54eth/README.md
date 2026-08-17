# LogicBeach: Powerful Moss (0.55 ETH, [OPEN])

LogicBeach, an anonymous glitch and downtempo artist, released their 6th album, "Powerful
Moss," on 2025-01-17 with a prize contract on Base holding ETH that grows over time and pays
out to whichever wallet a 12-word BIP39 seed derives. This is the artist's 3rd treasure hunt in
the same format: the first 2, "Bifurcations" (2020, Bitcoin) and a 2021 Ethereum puzzle, both
paid out to real solvers. I confirmed the carrier for this one is not the audio, unlike
"Bifurcations": it is a POAP badge image showing a clock face laid over the full alphabetical
BIP39 wordlist as wrapped text, where each hour's numeral marks a word and the 12 hours give
the order. 3 of the 12 hours read with no ambiguity; the other 9 are pinned to about 3
candidate words each because a numeral spans roughly 2 text rows on the only resolution the
image exists at. Over 3.3 million candidate 12-word combinations have been tested against the
winner wallet, all negative, and no higher-resolution source of the image is known to exist.

## At a glance

| | |
|---|---|
| Author | LogicBeach, [logicbeach.xyz](https://logicbeach.xyz/powerfulmoss) |
| Published | 2025-01-17, album and NFT drop ([puzzle page](https://logicbeach.xyz/powerfulmoss)) |
| Prize | 0.55 ETH held by the prize contract (about $1,034 at ETH = $1,880, 2026-08-16) |
| Chain | base |
| Escrow | `0x831102C7eb86f9EC8f79dF891bDeA187D54344Dd` ([explorer](https://basescan.org/address/0x831102C7eb86f9EC8f79dF891bDeA187D54344Dd)) |
| Last on-chain check | 2026-08-16: contract holds 0.55 ETH, winner wallet `0x635739254BDE27d28301f25aD57c3cAC3C3468f3` still at dust balance (0.006404376568548341 ETH) and outgoing transaction count 2, unchanged since the prior check |
| Status | OPEN |
| Puzzle type | image-stego, bip39-seed, word-selection, smart-contract |
| Target format | BIP39 12 words (English), BIP44 `m/44'/60'/0'/0/0`, no passphrase, address must equal the winner wallet |
| Certified oracle | yes: `tools/oracle.py --selftest` (certified against the public BIP39 KAT address and the artist's prior solved "Bifurcations" BIP84 vector) |
| What remains | an author-grounded mapping from the artwork geometry to exactly 12 ordered BIP39 wordlist cells; the native raster has no visible 1-through-12 clock-numeral layer |
| Series | none |

## The puzzle as published

The album has 12 tracks, listed exactly as published in the NFT's own metadata in
`data/tracks.json`. The NFT unlocks a download link, but the album is also freely downloadable
from the puzzle page. A POAP badge tied to the launch, drop "PowerfulMoss By LogicBeach.eth" (drop
id 183468, created 2025-01-10), carries the puzzle artwork: the complete alphabetical BIP39
wordlist rendered as wrapped monospace text, plus red plot axes and rays, a yellow title, and a
cursive signature. Earlier analysis treated the overlay as a 12-hour clock, but native-raster
inspection found no visible 1-through-12 numeral layer or ray-to-word-cell mapping. The prize
contract's own getters report a start time of 2025-01-17 20:00 UTC, a minimum claimable amount of
0.25 ETH, and a pot that grows toward the contract's full balance over time; an early withdrawal
forfeits the remainder to the contract's creator. Full quotes and links in
`clues/author-posts.md`.

![Historical 12-position grid hypothesis: 3 single reads in blue and 9 row-window candidate sets in orange](images/01-seed-grid.svg)
*Figure 1. Historical candidate grid tested against the winner wallet; the native image does not establish its 12 positions (source: data/seed-grid.json, script tools/fig_seed_grid.py), 2026-08-16.*

## What is understood

### Mechanism

The target is expected to be a 12-word BIP39 mnemonic deriving the winner wallet
under the standard Ethereum path `m/44'/60'/0'/0/0`, following the artist's 2021
puzzle precedent. The POAP background contains the full BIP39 wordlist in
alphabetical order, wrapped as monospace text at a measured row pitch of 48
pixels across 39 rows. Earlier searches imposed 12 clock positions and read the
wordlist cells at those positions. The native 2004x2011 raster does not contain
a visible 1-through-12 numeral layer, so those positions and their three
single-word reads are historical search hypotheses, not confirmed image facts.
The oracle remains valid once an author-grounded selector supplies 12 ordered
words.

### Derivation and oracle

```
python3 tools/oracle.py --selftest                 # must print SELFTEST OK
python3 tools/oracle.py "w1 w2 w3 w4 w5 w6 w7 w8 w9 w10 w11 w12"
python3 tools/oracle.py --stdin                     # one 12-word candidate per line
```

A candidate is validated as a BIP39 mnemonic, seeded, and swept across 9 nearby BIP44 paths (3
accounts times 3 indexes) to be anti-false-negative against a wallet imported at a non-default
account or index. It reports `MATCH <path> <address>` only on an exact match against the winner
wallet, `NO MATCH` otherwise.

### Certified against

`tools/oracle.py --selftest` reproduces the public BIP39 all-zero-entropy test vector at
`m/44'/60'/0'/0/0`, deriving `0x9858EfFD232B4033E47d90003D41EC34EcaEda94`; a positive control
confirms the oracle finds this same address when told to look for it; a negative control
confirms the same phrase does not match the real winner wallet; and an independent check
reproduces the artist's own solved "Bifurcations" seed at BIP84, deriving
`bc1qj7467e7r5pdfpypm03wyvguupdrld0ul2gcutg`, the address that received and fully spent 0.1058
BTC in that prior puzzle. Reproduced 2026-08-16.

### Established facts

1. The prize contract holds 0.55 ETH and the winner wallet remains at a dust balance with an
   unchanged outgoing transaction count, checked via `eth_getBalance` and
   `eth_getTransactionCount` against a public Base RPC endpoint on 2026-08-16. The pot grew
   from 0.54 to 0.55 ETH since the prior check, consistent with the contract's own time-based
   growth mechanism rather than a partial claim.
2. The prize is a contract balance, not a plain wallet: `eth_getBalance` must be read on the
   contract address, not on the winner wallet or the artist's separate `owner()` address, which
   controls minting and metadata only, not the pot.
3. The album's masters measure at close to 0 percent energy above 13 kHz, a property of the
   recording rather than a playback artifact, so the "Bifurcations" audio toolbox (which solved
   the artist's prior puzzle) finds nothing on all 12 tracks of this album: there is no high
   band left to carry spectrogram text.
4. The POAP image (`clues/powerfulmoss-poap.png`) contains one gray flow-text
   population, red plot axes and rays, and yellow title/signature elements. It
   has no visible 1-through-12 clock-numeral layer, distinctly marked word
   population, or ray-to-cell mapping.
5. No source of the plot finer than the published 2004x2011 raster is known to
   exist: checked against the prize contract's own `tokenURI`, the POAP asset
   server, the artist's website, and the album's video (1080p, lower resolution
   than the plot).
6. The artist's 2 prior puzzles in this format both paid out to real solvers: "Bifurcations"
   (2020) to `bc1qj7467e7r5pdfpypm03wyvguupdrld0ul2gcutg`, fully spent, and the 2021 ETH puzzle
   to a wallet now at 0 ETH, both confirmed on-chain.

## What has been tested

Full ledger in [analysis/tested.md](analysis/tested.md). Summary:

| Hypothesis | Space | Method | Result | Witness | Date |
|---|---|---|---|---|---|
| Full "Bifurcations" audio toolbox on all 12 lossless masters | 12 tracks | spectrogram, Morse, SSTV, LSB, ASR, source separation | 0 findings, high band physically empty | yes | 2026-06-17 |
| Historical POAP grid enumeration, 4 canonical orderings, row window plus 1 | 1,193,373 combinations (132,597 checksum-valid) | BIP44 path sweep | 0 match | yes | 2026-07-14 |
| Historical asymmetric row window per ordering | 531,441 combinations per ordering | same oracle | 0 match | yes | 2026-06-17 |
| Exactly one historical hour opened to a new +/-2 row, 4 canonical orderings | 1,495,908 combinations (93,069 checksum-valid) | same oracle, committed stream replay | 0 match | yes | 2026-08-16 |
| Native-raster viability audit of numeral-bottom-pixel and ray-length selectors | N=0 for each | byte-exact image inspection | no candidate stream exists | oracle selftest only; no candidates | 2026-08-16 |
| Distinct-overlay and higher-resolution-source hypotheses | full image | histogram analysis, source hunt | both refuted | yes | 2026-06-17 |

Cumulative: 4,815,045 candidate combinations from the historical grid
hypothesis tested against the winner wallet, 0 matches. The native-raster audit
shows that this grid is not an image-established selector. Lyric tokens on 2
tracks were deliberately not fed to the oracle because no mechanism selects
which 12 would form the seed.

## Open leads, ranked

1. **Recover an author-grounded twelve-cell geometry mapping** (external
   evidence). A published author statement, source asset, or independently
   verifiable legend must identify all 12 cells and their order before another
   bounded image-derived candidate stream exists.
2. **Resample at the numeral's bottom pixel instead of its centroid** (closed).
   The native raster has no 12 numeral glyph boxes, so this interpretation has
   N=0.
3. **Test the sunburst ray length as an alternative per-hour selector**
   (closed). Rays are visible, but the artwork supplies no hour anchors or
   ray-length-to-word-cell mapping, so this interpretation also has N=0.

Full notes: [analysis/leads.md](analysis/leads.md).

## Files in this folder

| Path | What it is |
|---|---|
| `clues/powerfulmoss-poap.png` | the published POAP artwork, byte-exact, sha256 recorded in puzzle.json |
| `clues/author-posts.md` | the author's published NFT metadata and launch-period quote, dated and linked |
| `data/tracks.json` | the album's 12 track titles, exactly as published in the NFT metadata |
| `data/seed-grid.json` | the historical 12-position grid hypothesis and its tested candidate words; not a native-image-established selector |
| `analysis/tested.md` | the complete negatives ledger |
| `analysis/leads.md` | full notes behind the 3 ranked leads |
| `images/01-seed-grid.svg` | figure for the historical grid hypothesis |
| `tools/oracle.py` | candidate checker, BIP44 path sweep, certified |
| `tools/fig_seed_grid.py` | generates images/01-seed-grid.svg from data/seed-grid.json |

## Sources

- LogicBeach, "Powerful Moss" puzzle page: https://logicbeach.xyz/powerfulmoss
- LogicBeach, launch-period tweet ("8 people have discovered the POAP"), 2025-01-24: https://x.com/Logic_Beach/status/1882824094854557885
- POAP drop "PowerfulMoss By LogicBeach.eth" (drop id 183468), checked 2026-08-16: https://poap.gallery/drops/183468
- "Bifurcations" solve write-up (prior puzzle, cited for method precedent, not part of this prize), checked 2026-08-16: https://elronvhubbard.medium.com/logic-beach-bifurcations-album-puzzle-write-up-1e1094d41038
- 2021 ETH puzzle write-up (prior puzzle, cited for method precedent, not part of this prize), checked 2026-08-16: https://l0gicbeach.medium.com/logicbeach-eth-album-puzzle-2021-57acaf1910db
- Prize contract, Basescan: https://basescan.org/address/0x831102C7eb86f9EC8f79dF891bDeA187D54344Dd
