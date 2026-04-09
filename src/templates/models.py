"""Pydantic models for ComfyUI workflow template index data."""

from pydantic import BaseModel, Field


class TemplateIO(BaseModel):
    """A single input or output specification for a template."""

    nodeId: int
    nodeType: str
    file: str = ""
    mediaType: str = ""


class TemplateIOSpec(BaseModel):
    """Input/output specification for a template."""

    inputs: list[TemplateIO] = []
    outputs: list[TemplateIO] = []


class Template(BaseModel):
    """A single workflow template from the index."""

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
    io: TemplateIOSpec = Field(default_factory=TemplateIOSpec)
    thumbnail: list[str] = []


class TemplateCategory(BaseModel):
    """A category grouping from the template index."""

    moduleName: str = ""
    category: str = ""
    icon: str = ""
    title: str = ""
    type: str = ""
    isEssential: bool = False
    templates: list[Template] = []


class TemplateSummary(BaseModel):
    """Lightweight template reference for cross-reference results."""

    name: str
    title: str
    mediaType: str = ""
    tags: list[str] = []
    category: str = ""
