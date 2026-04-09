# comfy-templates Gotchas

## Fuzzy Matching Surprises
Cross-reference falls back to fuzzy matching when exact match returns nothing. This can surface unexpected results -- always check the match type in output.

## fetch_all_nodes Pagination
`fetch_all_nodes` uses a `pages` parameter. Don't assume single-page responses -- the full template list may span multiple pages.

## Gap Scoring Formula
`log10(downloads) * (1 + log2(stars) * 0.5)` balances download volume with community signal (stars). A pack with 100K downloads but 0 stars scores lower than expected.

## Coverage Is Pack-Level
Coverage percentage measures unique packs referenced in `requiresCustomNodes` across all templates, divided by total registry packs. It does NOT measure individual node coverage within packs.

## Cache Behavior
Template and registry data share the same `DiskCache` singleton. Use `--refresh` to force re-fetch. Stale cache can cause cross-reference mismatches if templates were recently added upstream.
