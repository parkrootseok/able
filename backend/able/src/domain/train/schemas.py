from typing import List, Dict, Any
from pydantic import Field
from pydantic.v1 import ConfigDict

from src.common.utils.response.schemas import ImmutableBaseModel
from matplotlib.figure import Figure

from src.domain.train.enums import TrainStatus


class PerformanceMetrics(ImmutableBaseModel):
    accuracy: float
    top5_accuracy: float
    precision: float
    recall: float

class Loss(ImmutableBaseModel):
    training: float
    validation: float

class Accuracy(ImmutableBaseModel):
    accuracy: float

class EpochResult(ImmutableBaseModel):
    epoch: str
    losses: Loss
    accuracies: Accuracy

class HyperParameter(ImmutableBaseModel):
    batch_size: int
    epoch: int

class GetHyperParameter(ImmutableBaseModel):
    hyper_parameter: HyperParameter

class SaveHyperParameter(ImmutableBaseModel):
    hyper_parameter: HyperParameter

class TrainResultResponse(ImmutableBaseModel):
    confusion_matrix: str
    performance_metrics: PerformanceMetrics
    f1_score: str
    epoch_result: List[EpochResult]

class TrainResultMetrics(ImmutableBaseModel):
    performance_metrics: PerformanceMetrics
    f1: float
    confusion_matrix: Figure

    model_config = ConfigDict(arbitrary_types_allowed=True)

class TrainResultMetadata(ImmutableBaseModel):
    data_path: str = Field(..., description="데이터셋의 경로")
    # input_shape: List[int] = Field(..., description="입력 데이터 형상")
    classes: List[str] = Field(..., description="클래스 목록")
    status: TrainStatus