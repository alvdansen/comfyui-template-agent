# comfy-discover Gotchas

## GitHub API Rate Limits
Unauthenticated: 60 requests/hour. Set `GITHUB_TOKEN` env var for higher limits. The `get_github_client()` in `src/shared/http.py` picks it up automatically.

## httpx follow_redirects
GitHub API returns 301 on `/contents` endpoint. The GitHub client uses `follow_redirects=True` but the registry client does not -- don't mix them up.

## Registry Tags Are Empty
Most packs have an empty `tags` field. Category filtering uses keyword matching via `classify_node()` against the name and description instead.

## Cache TTLs
- Browsing (highlights): 1 hour
- Search: 15 minutes
- Specs: 24 hours
- Use `--refresh` to bypass cache

## search_by_type Two-Step
`search_by_type` first searches packs by name/description, then verifies I/O types via a second call to the comfy-nodes API. This means it's slower than text search and makes 2x API calls.

## fetch_all_nodes Pagination
`fetch_all_nodes(pages=6)` fetches 6 pages of 50 nodes each. If the registry grows beyond 300 active packs, increase the `pages` parameter or results will be incomplete.

## Random Mode Weighting
Default random mode is weighted by downloads + stars. Use `--truly-random` for unbiased sampling. Weighted mode can loop up to `limit * 10` attempts for deduplication.
