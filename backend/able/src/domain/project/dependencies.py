from src.domain.project.service import ProjectService
from src.domain.project.repository import ProjectRepository
from src.common.utils.file.path_manager import PathManager

def get_project_service() -> ProjectService:
    repository = ProjectRepository(path_manager=PathManager())
    return ProjectService(repository=repository)
