from fastapi import APIRouter, BackgroundTasks
from starlette.responses import Response

from .dto import TrainResultRequest, TrainRequest
from .service import train_in_background, load_train_result, get_device_list
from src.train.schemas import TrainResultResponse
from src.response.utils import ok
from ..response.schemas import ResponseModel
from ..response.utils import accepted

train_router = router = APIRouter()

@router.get(
    path="/result/{project_name}/{train_result_name}",
    response_model=ResponseModel[TrainResultResponse],
    summary="학습 결과 조회",
    description="프로젝트 이름, 학습 결과 이름에 대하여 조회한다."
)
def get_train_result(project_name: str, train_result_name: str):
    return ok(
        data=TrainResultResponse(
            train_result=load_train_result(project_name, train_result_name)
        )
    )


@router.post("")
async def train(request: TrainRequest, background_tasks: BackgroundTasks) -> Response:
    background_tasks.add_task(train_in_background, request)
    return accepted()

@router.get("/devices")
def get_devices():
    return ok(
        data=get_device_list()
    )