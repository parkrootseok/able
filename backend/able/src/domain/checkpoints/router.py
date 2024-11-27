import src.domain.checkpoints.service as service

from fastapi import APIRouter, status, Query

from src.domain.checkpoints.schemas import CheckpointListResponse, CheckpointsPaginatedResponse
from src.common.utils.response.schemas import ResponseModel
from src.common.utils.response.utils import created, ok, no_content, bad_request

checkpoint_router = router = APIRouter()

@router.post("/{project_name}/{result_name}", response_model=ResponseModel[CheckpointListResponse],
             summary="checkpoints 목록 조회", description="")
async def create_project(project_name: str, result_name: str):

    result = service.get_all_checkpoints(project_name, result_name)

    return ok(
        data=result
    )

@router.get("", response_model=ResponseModel[CheckpointsPaginatedResponse],
            summary="checkpoints 목록 조회(train_best, valid_best, final 제외)", description="무한 스크롤")
async def get_checkpoints(project_name: str, result_name: str,
                    index: int = Query(..., description="몇 번째 스크롤인지"),
                    size: int = Query(..., description="스크롤 한 번에 가져올 아이템 개수")):
    response = service.get_paginated_checkpoints(project_name, result_name, index, size)
    if response.checkpoints is None:
        return bad_request()
    if len(response.checkpoints) == 0:
        return no_content()
    return ok(data=response)

@router.get("/search",
            response_model=ResponseModel[CheckpointsPaginatedResponse],
            summary="checkpoint 검색")
async def search_checkpoint(project_name: str, result_name:str, keyword: str, index: int, size: int):
    response = service.search_checkpoint(project_name, result_name, keyword, index, size)
    if response.checkpoints is None:
        return bad_request()
    if(len(response.checkpoints) == 0):
        return no_content()
    return ok(data=response)