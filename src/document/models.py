"""Pydantic models for documentation generation."""

from pydantic import BaseModel, Field


class IOItem(BaseModel):
    """A single input or output node in a workflow."""

    nodeId: int
    nodeType: str
    fieldName: str = ""
    mediaType: str = ""


class IOSpec(BaseModel):
    """Input/output specification extracted from a workflow."""

    inputs: list[IOItem] = []
    outputs: list[IOItem] = []


class IndexEntry(BaseModel):
    """A complete index.json entry for a workflow template."""

    name: str
    title: str
    description: str = ""
    mediaType: str = ""
    mediaSubtype: str = ""
    tags: list[str] = []
    models: list[str] = []
    requiresCustomNodes: list[str] = []
    date: str = ""
    openSource: bool = True
    size: int = 0
    vram: int = 0
    usage: int = 0
    searchRank: int = 0
    username: str = ""
    io: IOSpec = Field(default_factory=IOSpec)
    thumbnail: list[str] = []


class NotionSubmission(BaseModel):
    """Data for a Notion submission form."""

    template_name: str
    title: str
    description: str
    models: list[str]
    custom_nodes: list[str]
    io_summary: str
    thumbnail_notes: str
    workflow_link: str = ""
