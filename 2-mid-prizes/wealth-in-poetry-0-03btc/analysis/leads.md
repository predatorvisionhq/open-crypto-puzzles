# Lead analysis: Wealth in Poetry

## Closed: read the purported cipher table on the Steganographia illustration ($N=0$)

The exact public image used in the Medium article is
`https://miro.medium.com/v2/resize:fit:4448/1*tP7U5Tpv7oA5eklwA36tyQ.png`
(4448×2555). Direct visual inspection establishes that it is an open book whose right-hand page
is a Steganographia title page, not a cipher-table page. It has title/dedication/imprint layout
and a single Roman-numeral publication date; neither page has a numeric grid, ordered sequence,
table, position index, or declared extraction rule.

The published Trithemian mechanism requires such a key to select positions. Reading digits,
letters, coordinates, or an order into this illustration would impose an unbounded external rule,
so it cannot produce a deterministic bounded seed family. The lead is therefore killed precisely
at $N=0$: no candidate was created and no oracle comparison was applicable. No third-party image
or text was copied into this repository.

## Closed: old-Electrum replay ($N=0$)

The only shipped materials are the README, this analysis, the negatives ledger, and the two
worked examples in `clues/author-posts.md`; there is no target-local derivation code, archived
article/token corpus, or exact candidate list. The prior ledger records an old-Electrum v1/v2
sweep over four example seeds, but it names rather than supplies the complete four-member corpus.

The two publicly quoted examples cannot repair that gap: replaying either would repeat the
already-recorded old-Electrum family, while reconstructing the other two or introducing new
selectors would create an unbounded, undocumented corpus. A target-local oracle is therefore not
implemented: there is neither an exact untested candidate corpus to run nor an existing
target-address comparison path it could reproduce. This lead is killed at $N=0$ with no loop,
oracle invocation, or candidate material.

## Closed: target-local oracle certification ($N=0$)

This target ships no derivation source, executable, candidate corpus, or target-local
address-comparison path. The required self-test invocation, `python3 tools/oracle.py --selftest`,
fails because `tools/oracle.py` is absent. A public old-Electrum v1 known-answer vector could
only certify a new, unrelated implementation; it cannot certify an absent target solver or make
the unavailable old-Electrum corpus exact.

Accordingly no oracle scaffold or synthetic substitute is added. There is no executable family to
benchmark or run, so this prerequisite also closes at $N=0$ and does not create a ledger row.
