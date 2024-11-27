from fastapi import APIRouter, Depends, Response

from src.domain.deploy.dependencies import get_deploy_service
from src.domain.deploy.schema.response import StopApiResponse, RegisterApiResponse, RemoveApiResponse, \
    GetApisResponse, DeployInfoResponse
from src.domain.deploy.service import DeployService
from src.domain.deploy.schema.request import RegisterApiRequest
from src.common.utils.response.utils import accepted, ok, no_content, bad_request
from src.common.utils.response.schemas import ResponseModel

deploy_router = router = APIRouter()

@router.get("/run")
def run(service: DeployService = Depends(get_deploy_service)) -> Response:
    service.run()
    return accepted()

@router.get("/stop")
def stop(service: DeployService = Depends(get_deploy_service)) -> Response:
    service.stop()
    return accepted()

@router.post("/restart")
def restart(
    service: DeployService = Depends(get_deploy_service)
) -> Response:
    service.stop()
    service.run()
    return accepted()

@router.post(
    path="/apis",
    response_model=ResponseModel[RegisterApiResponse],
)
def register_api(
    request: RegisterApiRequest,
    service: DeployService = Depends(get_deploy_service)
) -> Response:
    return ok(data=RegisterApiResponse(is_success=service.register_api(request)))

@router.put(
    path="/apis",
    response_model=ResponseModel[StopApiResponse],
)
def stop_api(
        uri: str,
        service: DeployService = Depends(get_deploy_service)
) -> Response:
    return ok(data=StopApiResponse(is_success=service.stop_api(uri)))


@router.delete(
    path="/apis",
    response_model=ResponseModel[RemoveApiResponse],
)
def remove_api(
        uri: str,
        service: DeployService = Depends(get_deploy_service)
) -> Response:
    return ok(data=RemoveApiResponse(is_success=service.remove_api(uri)))

@router.get(
    path="/apis",
    response_model=ResponseModel[GetApisResponse],
    summary="배포된 API 리스트 조회")
def get_apis(
        page: int = 0,
        page_size: int = 10,
        service: DeployService = Depends(get_deploy_service)
) -> Response:
    result = service.get_apis(page, page_size)

    if len(result.apis) == 0:
        return no_content()

    return ok(data=result)

@router.get("/info",
            response_model=ResponseModel[DeployInfoResponse],
            summary="정보")
def get_info(service: DeployService = Depends(get_deploy_service)) -> Response:
    result = service.get_info()
    return ok(data=result)