from typing import List, Optional
from src.response.schemas import ImmutableBaseModel

class ClassScore(ImmutableBaseModel):
    class_name: str
    class_score: int

class ClassScores(ImmutableBaseModel):
    class_scores: List[ClassScore]

class FeatureMap(ImmutableBaseModel):
    block_id: str
    img: Optional[str]

class CheckpointResponse(ImmutableBaseModel):
    epochs : Optional[List[str]]
    has_next: bool

class AnalyzeResponse(ImmutableBaseModel):
    image: str
    class_scores: List[ClassScore]

class FeatureMapRequest(ImmutableBaseModel):
    project_name: str
    result_name: str
    epoch_name: str
    block_id: List[str]

class FeatureMapResponse(ImmutableBaseModel):
    feature_map: List[FeatureMap]
