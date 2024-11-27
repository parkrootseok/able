from src.common.utils.response.schemas import ImmutableBaseModel
from src.domain.deploy.schema.dto import ApiInformation

class RegisterApiResponse(ImmutableBaseModel):
    is_success: bool

class StopApiResponse(ImmutableBaseModel):
    is_success: bool

class RemoveApiResponse(ImmutableBaseModel):
    is_success: bool

class GetApisResponse(ImmutableBaseModel):
    total_pages: int
    apis: list[ApiInformation]

class DeployInfoResponse(ImmutableBaseModel):
    api_version: str
    port: str
    status: str