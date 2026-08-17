# Open leads, full notes

Ranked summary is in the README. This file has the reasoning behind the ranking.

## 1. Reconstruct the 2019 browser-copy rendering of the Wattpad chapter

The author states she typed the chapter with a blank line between paragraphs
("two line breaks... one 13 and one 10 for each"), but the chapter's current
storage (fetched through Wattpad's API, `modifyDate` 2019-07-23, matching the
2019-07-30 funding of the current escrow) contains no blank paragraphs at all:
Wattpad's storage format normalizes them away. What she actually hashed was most
likely whatever her browser produced when she selected and copied the rendered
page in 2019, not the raw API storage read today. A first attempt at simulating
this (Chromium's `selection.toString` and `innerText` rendering rules) is
included in the "simulated browser copy" row of `analysis/tested.md`, but it
used only one rendering assumption; the actual 2019 Wattpad reader page layout
(paragraph spacing, non-breaking spaces around punctuation, title block) has not
been reconstructed and tested as its own base text.

What would confirm it: rendering `data/chapitre_second_page.html` the way a 2019
browser would have displayed it, extracting the resulting paragraph text, and
running it (with the certified case-flip rule applied to the same candidate
paragraph groups already tested) through `tools/oracle.py`.
What would kill it: a faithful reconstruction still not matching after the
already-tested paragraph-selection hypotheses are re-applied to it.
Cost: hours, mostly in getting the 2019 rendering right; the derivation itself is
seconds per candidate.

## 2. Read the 27 posts and comments between the rehash and the shutdown

The author rehashed and refunded the Real Big Block on 2019-07-30, then stopped
posting shortly after. The 27 posts and comments she made between 2019-07-30 and
2019-08-04 have been read once for an explicit "twist" statement, but not
re-read systematically against the current, narrower list of untested paragraph
combinations.

What would confirm it: a stated detail (an extra modification, a further
paragraph, a corrected count) that, applied to the certified rule and re-tested,
matches the address.
What would kill it: a full re-read producing no new candidate paragraph or rule
variant beyond what `analysis/tested.md` already covers.
Cost: an hour of reading.

## 3. Two-character edits on the strongest base texts

The single-character-edit sweep (266,038,400 candidates, `analysis/tested.md`)
covers every one-character difference from 40 base texts and is exhaustive for
that distance. It does not cover 2-character differences, which would catch a
base text that is off by, for example, one inserted invisible character AND one
capitalization slip. A 2-character sweep restricted to the small set of NBSP and
line-ending pairs (rather than all positions) is a bounded space, not a full
40-base x 2-character search.

What would confirm it: a match within the bounded 2-character space.
What would kill it: exhausting that bounded space with 0 match; the full,
unbounded 2-character space is not proposed here, since its cost is
disproportionate without a narrower reason to expect the answer lives there.
Cost: on the order of an hour on a rented GPU for the bounded version described
above; the private research folder priced this at roughly 45 minutes per base
text for a similarly scoped variant.

## 4. Identify what "76" indexes for Block 76

The recovered public submission corpus now eliminates the named r/Grycoin
candidate deterministically. The chronological query
`author=AoiNakamoto`, `subreddit=Grycoin`, sorted ascending by `created_utc`,
contains 87 submission objects. Its item 76 is `ce4ixs`, Quizchain2 Block 71;
the exact answer/TOMI pair published in that record fails both Block-76 MD5
prefixes and the certified address oracle. Restricting the same corpus to
original self-posts leaves only 71 records, so that convention has no
position-76 candidate at all.

This closes the author's-r/Grycoin-submissions corpus, including the only
natural cross-post convention. It does not identify the corpus meant by the
block number. The still-untried, separately bounded public corpora are a fuller
Hal Finney tweet archive and Satoshi SourceForge material; any proposed
whitepaper/source-code unitization must first define a stable, public numbering
rule rather than generate variants.

## 5. A short, human-reasoned answer to "change to" / "from change to"

The shipped Block-76 record preserves the question exactly as `change to` and
the update exactly as changing it "from 'change to' to 'from change to'." The
recovered public discussion supplies one further disambiguation: when asked
"to or two?", the author answered "to." This rules out the homophone reading,
but does not state a solution or a TOMI value. It therefore produces no new
deterministic candidate pair (N = 0); the already-tested literal-post-string
family must not be repeated.

The author had said that Block 54 would also hint at Block 76, but the public
statement provides no rule that maps that earlier solved block to one answer
and one TOMI field. The remaining ambiguity is a genuinely human semantic
reading of the prepositional `from ... to` construction, not a justified
dictionary expansion. This lead remains open for a specific, evidence-backed
pair.
