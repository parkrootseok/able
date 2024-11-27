from src.domain.deploy.enums import ApiStatus
from src.common.utils.response.schemas import ImmutableBaseModel

class ApiInformation(ImmutableBaseModel):
    project_name: str
    train_result: str
    checkpoint: str
    uri: str
    description: str
    status: ApiStatus