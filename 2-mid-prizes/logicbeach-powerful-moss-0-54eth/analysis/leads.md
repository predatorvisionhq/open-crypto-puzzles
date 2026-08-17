# Open leads, ranked

## 1. Recover an author-grounded twelve-cell geometry mapping (external evidence)

The native raster contains the wordlist and plot-like overlay but no visible
one-through-twelve numeral layer.  A published author statement, source asset,
or independently verifiable legend that maps twelve artwork positions to
wordlist cells is needed before a bounded candidate stream can exist.  It
confirms if it names all twelve cells and their order; absent that mapping,
row-window widening is not a testable selector.

## 2. Resample at the numeral's bottom pixel instead of its centroid - closed

This selector has no native-image input.  The byte-exact published raster
(`6742c3c85987e6509d8e9c4691c740dddc2b43d5c469eb47e5044da9a6ea985d`) does
not contain a visible set of twelve serif clock numerals over the wordlist.
Its sparse red labels are coordinate/scale labels attached to the plot axes and
ray/grid overlay, rather than one `1` through `12` label at each clock
position.  Thus there are no twelve numeral glyph bounding boxes, and no
bottom pixels from which to read twelve rows.  The bounded candidate space is
`N=0`; no candidate generator or oracle run is justified.

## 3. Test the sunburst ray length as an alternative per-hour selector - closed

The native artifact does show red radial rays, but it supplies neither twelve
hour anchors nor a mapping from a ray's length to a wordlist row or column.
Treating every ray as an hour, pairing rays, or choosing a rank-to-row mapping
would each add an arbitrary rule not present in the artwork.  Consequently no
per-hour selection function can be derived directly from the image and this
lead also has `N=0`; no search was generated.

The next unresolved prerequisite is an author-grounded mapping from artwork
geometry to exactly twelve wordlist cells.  Until one exists, the earlier
numeral-overlay and widened-row work has no native selector to extend.

Full ledger: [tested.md](tested.md).
