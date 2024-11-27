from src.domain.deploy.enums import ApiStatus
from src.common.utils.response.schemas import ImmutableBaseModel

class Project(ImmutableBaseModel):
    title: str
    description: str | None = None
    cuda_version: str  | None = None
    python_kernel_path: str | None = None
    thumbnail: str | None = None