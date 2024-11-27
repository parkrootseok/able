from src.common.utils.response.schemas import ImmutableBaseModel

class TrainSummary(ImmutableBaseModel):
    index: int
    origin_dir_name: str
    date: str
    accuracy: str
    status: str

class TrainLogResponse(ImmutableBaseModel):
    total_pages: int
    train_summaries: list[TrainSummary]