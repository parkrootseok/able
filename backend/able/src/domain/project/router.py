from fastapi import APIRouter, Depends
from src.domain.project.dependencies import get_project_service
from src.domain.project.schema.request import CreateProjectRequest, UpdateProjectRequest
from src.domain.project.schema.response import DeleteProjectResponse, UpdateProjectResponse, ProjectResponse, ProjectsResponse
from src.domain.project.service import ProjectService
from src.common.utils.response.schemas import ResponseModel
from src.common.utils.response.utils import created, ok

project_router = router = APIRouter()

@router.post(
    path="",
    response_model=ResponseModel,
    summary="프로젝트 생성"
)
async def create_project(
    request: CreateProjectRequest,
    service: ProjectService = Depends(get_project_service)
):
    service.create_project(request)
    return created()


@router.get(
    path="/{title}",
    response_model=ResponseModel[ProjectResponse],
    summary="프로젝트 단일 조회",
)
async def get_project(
    title: str,
    service: ProjectService = Depends(get_project_service)
):
    project = service.get_project(title)
    return ok(data=project)


@router.get(
    path="/",
    response_model=ResponseModel[ProjectsResponse],
    summary="프로젝트 목록 조회",
    description="",
)
async def get_projects(
    service: ProjectService = Depends(get_project_service)
):
    projects = service.repository.get_metadata_list()
    return ok(data=ProjectsResponse(count=len(projects), projects=projects))


@router.put(
    path="",
    response_model=ResponseModel[UpdateProjectResponse],
    summary="프로젝트 정보 수정",
    description="변경 전 프로젝트 이름, 설명 포함 필요"
)
async def update_project(
    title: str,
    request: UpdateProjectRequest,
    service: ProjectService = Depends(get_project_service)
):
    is_success = service.update_project(title, request)
    return ok(data=UpdateProjectResponse(is_success=is_success))


@router.delete(
    path="",
    response_model=ResponseModel[DeleteProjectResponse],
    summary="프로젝트 삭제",
    description="프로젝트 이름으로 삭제"
)
async def delete_project(
    title: str,
    service: ProjectService = Depends(get_project_service)
):
    is_success = service.delete_project(title)
    return ok(data=DeleteProjectResponse(is_success=is_success))
