from typing import List
from src.common.utils.response.schemas import ImmutableBaseModel

class ProjectResponse(ImmutableBaseModel):
    title: str
    description: str | None = None
    cuda_version: str  | None = None
    python_kernel_path: str | None = None
    thumbnail: str | None = None

class ProjectsResponse(ImmutableBaseModel):
    count: int
    projects: List[str]

class UpdateProjectResponse(ImmutableBaseModel):
    is_success: bool

class DeleteProjectResponse(ImmutableBaseModel):
    is_success: bool


