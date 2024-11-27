from src.common.utils.response.schemas import ImmutableBaseModel

class CreateProjectRequest(ImmutableBaseModel):
    title: str
    description: str
    cuda_version: str
    python_kernel_path: str

class UpdateProjectRequest(ImmutableBaseModel):
    title: str
    description: str
    cuda_version: str
    python_kernel_path: str

