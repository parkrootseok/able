from typing import List, Optional
from src.common.utils.response.schemas import ImmutableBaseModel

class ClassScore(ImmutableBaseModel):
    class_name: str
    class_score: int

class ClassScores(ImmutableBaseModel):
    class_scores: List[ClassScore]

class AnalysisResult(ImmutableBaseModel):
    class_scores: List[ClassScore]
    heatmap_block_id: str

class FeatureMap(ImmutableBaseModel):
    block_id: str
    img: Optional[str]

class CheckpointResponse(ImmutableBaseModel):
    epochs : Optional[List[str]]
    has_next: bool

class AnalyzeResponse(ImmutableBaseModel):
    image: str
    class_scores: List[ClassScore]
    heatmap_block_id: str

class FeatureMapRequest(ImmutableBaseModel):
    project_name: str
    result_name: str
    epoch_name: str
    block_id: str

class FeatureMapResponse(ImmutableBaseModel):
    feature_map: str

class HeatMapResponse(ImmutableBaseModel):
    original_img: str
    heatmap_img: str
    class_scores: List[ClassScore]
    heatmap_block_id: str