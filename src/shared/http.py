"""Shared httpx client wrapper with configured timeouts and headers."""

import httpx

from src.shared.config import BASE_URL, CLIENT_TIMEOUT, USER_AGENT


def get_client() -> httpx.Client:
    """Return an httpx client configured for the ComfyUI registry API."""
    return httpx.Client(
        base_url=BASE_URL,
        timeout=CLIENT_TIMEOUT,
        headers={"User-Agent": USER_AGENT},
    )


def fetch_json(client: httpx.Client, path: str, params: dict | None = None) -> dict:
    """Fetch JSON from the given path, raising on HTTP errors."""
    response = client.get(path, params=params)
    response.raise_for_status()
    return response.json()
