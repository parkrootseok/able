from src.common.utils.utils import json_to_str, encode_image_to_base64
from src.common.utils.logger.utils import get_logger
from src.common.utils.file.exceptions import FileNotFoundException
from src.domain.project.exceptions import ProjectNameAlreadyExistsException
from src.domain.canvas.schemas import Canvas
from src.domain.project.schema.dto import Project
from src.domain.project.schema.response import ProjectResponse
from src.domain.project.schema.request import UpdateProjectRequest, CreateProjectRequest

class ProjectService:
    def __init__(self, repository):
        self.repository = repository
        self.logger = get_logger(self.__class__.__name__)

    def create_project(self, request: CreateProjectRequest) -> bool:
        self.logger.info(f"Starting creation of project: {request.title}")
        project_path, train_results_path = self.repository.create_project_directories(request.title)

        if not project_path or not train_results_path:
            self.logger.error(f"Project creation failed for: {request.title}")
            raise ProjectNameAlreadyExistsException("A project with the same name already exists.")

        self.repository.save_block_graph(project_path, json_to_str(Canvas()))
        return self.repository.save_metadata(project_path, request.model_dump())

    def get_project(self, title: str) -> ProjectResponse:
        self.logger.info(f"Retrieving project: {title}")
        metadata = self.repository.get_metadata(title)
        project = ProjectResponse.model_validate(metadata)

        try:
            thumbnail = self.repository.get_thumbnail(title)
            project.thumbnail = encode_image_to_base64(thumbnail)
        except FileNotFoundException:
            self.logger.warning(f"Thumbnail not found for project: {title}")
            project.thumbnail = None

        return project

    def update_project(self, title: str, request: UpdateProjectRequest) -> bool:
        self.logger.info(f"Updating project: {title} -> {request.title}")
        if title != request.title:
            self.repository.rename_project(title, request.title)

        updated_project = Project(**request.model_dump())
        return self.repository.save_metadata(
            self.repository.path_manager.get_projects_path(request.title),
            updated_project.model_dump()
        )

    def delete_project(self, title: str) -> bool:
        self.logger.info(f"Deleting project: {title}")
        return self.repository.delete_project(title)
