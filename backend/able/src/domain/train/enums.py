from enum import Enum

class TrainStatus(str, Enum):
    COMPLETE="완료"
    RUNNING="진행 중"
    FAIL="실패"