from src.common.utils.response.schemas import ImmutableBaseModel

class RegisterApiRequest(ImmutableBaseModel):
    project_name: str
    train_result: str
    checkpoint: str
    uri: str
    description: str
