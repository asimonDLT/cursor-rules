from pydantic import BaseModel, Field


class Tool(BaseModel):
    tool_id: str = Field(..., description="Unique identifier for the tool")
    name: str = Field(..., description="Display name of the tool")
    category: str = Field(
        ..., description="Category of the tool (e.g., martech, analytics)"
    )
    domains: list[str] = Field(
        default_factory=list, description="List of domains this tool is relevant to"
    )
    description: str | None = Field(None, description="A brief description of the tool")


class Role(BaseModel):
    role_id: str = Field(..., description="Unique identifier for the role")
    name: str = Field(..., description="Display name of the role")
    seniority: str | None = Field(
        None, description="Seniority level (e.g., c-level, director)"
    )
    scope: str | None = Field(
        None, description="Scope of the role (e.g., global, regional)"
    )
    span_of_control: int | None = Field(
        None, description="Approximate number of people managed"
    )
    domains: list[str] = Field(
        default_factory=list, description="List of primary domains of expertise"
    )
    primary_tools: list[str] = Field(
        default_factory=list, description="List of primary tool IDs used in this role"
    )
    frameworks: list[str] = Field(
        default_factory=list, description="List of frameworks or methodologies used"
    )
    description: str | None = Field(None, description="A brief description of the role")


class Domain(BaseModel):
    domain_id: str = Field(..., description="Unique identifier for the domain")
    name: str = Field(..., description="Display name of the domain")
    description: str | None = Field(
        None, description="A brief description of the domain"
    )
