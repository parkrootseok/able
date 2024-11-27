import src.domain.canvas.service as service

from fastapi import APIRouter
from src.domain.canvas.schemas import GetCanvasResponse, SaveCanvasRequest
from src.common.utils.response.schemas import ResponseModel
from src.common.utils.response.utils import ok, created, no_content

canvas_router = router = APIRouter()

@router.get(
    path="",
    response_model=ResponseModel[GetCanvasResponse],
    summary="캔버스 조회",
    description="현재 사용자가 생성중인 블록 그래프를 조회한다."
)
def get_canvas(project_name: str):
    canvas = service.get_canvas(project_name)

    if not canvas.blocks and not canvas.edges:
        return no_content()

    return ok(data=GetCanvasResponse(canvas=canvas))

@router.post(
    path="",
    summary="캔버스 저장",
    description="현재 사용자가 생성중인 블록 그래프 저장한다."
)
def save_canvas(project_name: str, canvas: SaveCanvasRequest):
    service.save_block_graph(project_name, canvas)
    return created()

