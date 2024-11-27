import src.domain.block.service as service
from fastapi import APIRouter
from src.domain.block.enums import BlockType
from src.domain.block.schemas import BlocksResponse, BlockResponse
from src.common.utils.response.schemas import ResponseModel
from src.common.utils.response.utils import ok

block_router = router = APIRouter()

@router.get(
    path="",
    response_model=ResponseModel[BlocksResponse],
    summary="타입별 블록 조회",
    description="해당 타입을 가진 블록 목록을 조회한다."
)
def find_blocks_by_type(type: BlockType):
    return ok(
        data=BlocksResponse(
            blocks=service.find_blocks_by_type(type)
        )
    )

@router.get(
    path="/search",
    response_model=ResponseModel[BlockResponse],
    summary="블록 검색",
    description="키워드를 가지는 블록에 대하여 검색한다."
)
def search(keyword: str):
    return ok(
        data=BlockResponse(
            block=service.search(keyword)
        )
    )