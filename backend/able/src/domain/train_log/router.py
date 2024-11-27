import src.domain.train_log.service as service
from fastapi import APIRouter

from src.common.utils.response.schemas import ResponseModel
from src.common.utils.response.utils import no_content, ok, bad_request
from src.domain.train_log.schemas import TrainLogResponse

train_log_router = router = APIRouter()

@router.get(
    path="/{project_name}/train/logs",
    response_model=ResponseModel[TrainLogResponse],
    summary="프로젝트 학습 기록 조회",
    description="프로젝트 이름으로 학습 기록 조회"
)
def get_train_logs(project_name: str, page: int, page_size: int):
    result = service.get_train_logs(project_name, page, page_size)

    if result is None:
        return bad_request()

    if len(result.train_summaries) == 0:
        return no_content()

    return ok(
        data=result
    )

