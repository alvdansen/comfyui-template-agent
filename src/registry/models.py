"""Pydantic models for ComfyUI Registry API responses."""

import json

from pydantic import BaseModel, ConfigDict, Field


class NodePack(BaseModel):
    """A node pack from the registry /nodes endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    author: str = ""
    description: str = ""
    downloads: int = 0
    github_stars: int = Field(0, alias="github_stars")
    rating: float = 0
    created_at: str = ""
    repository: str = ""
    tags: list[str] = []
    status: str = ""
    icon: str = ""


class ComfyNode(BaseModel):
    """An individual node from the /comfy-nodes endpoint."""

    comfy_node_name: str
    category: str = ""
    input_types: str = ""
    return_types: str = ""
    return_names: str = ""
    deprecated: bool = False
    experimental: bool = False

    def parsed_input_types(self) -> dict:
        """Parse the JSON-encoded input_types string."""
        if not self.input_types:
            return {}
        try:
            return json.loads(self.input_types)
        except (json.JSONDecodeError, TypeError):
            return {}

    def parsed_return_types(self) -> list:
        """Parse the JSON-encoded return_types string."""
        if not self.return_types:
            return []
        try:
            return json.loads(self.return_types)
        except (json.JSONDecodeError, TypeError):
            return []


class SearchResult(BaseModel):
    """Paginated response from /nodes endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    nodes: list[NodePack]
    total: int
    page: int
    limit: int
    totalPages: int = Field(0, alias="totalPages")


class ComfyNodeResult(BaseModel):
    """Response from /comfy-nodes endpoint."""

    comfy_nodes: list[ComfyNode]
    total: int
