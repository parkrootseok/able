from pathlib import Path
from src.common.utils.file.utils import create_directory, create_file, get_file, delete_directory, rename_path, read_image_file
from src.common.utils.file.constants import METADATA, BLOCK_GRAPH, THUMBNAIL
from src.common.utils import str_to_json, json_to_str
from src.common.utils.logger.utils import get_logger


class ProjectRepository:
    def __init__(self, path_manager):
        self.path_manager = path_manager
        self.logger = get_logger(self.__class__.__name__)

    def create_project_directories(self, title: str) -> tuple[Path, Path]:
        project_path = self.path_manager.get_projects_path(title)
        train_results_path = self.path_manager.get_train_results_path(title)

        if create_directory(train_results_path):
            self.logger.info(f"Created directories for project: {title}")
            return project_path, train_results_path
        else:
            self.logger.error(f"Failed to create directories for project: {title}")
            return None, None

    def save_metadata(self, project_path: Path, metadata: dict) -> bool:
        metadata_path = project_path / METADATA
        success = create_file(metadata_path, json_to_str(metadata))
        if success:
            self.logger.info(f"Saved metadata at: {metadata_path}")
        else:
            self.logger.error(f"Failed to save metadata at: {metadata_path}")
        return success

    def save_block_graph(self, project_path: Path, block_graph_data: str) -> bool:
        block_graph_path = project_path / BLOCK_GRAPH
        success = create_file(block_graph_path, block_graph_data)
        if success:
            self.logger.info(f"Saved block graph at: {block_graph_path}")
        else:
            self.logger.error(f"Failed to save block graph at: {block_graph_path}")
        return success

    def get_metadata(self, title: str) -> dict:
        metadata_path = self.path_manager.get_projects_path(title) / METADATA
        self.logger.debug(f"Retrieving metadata for project: {title}")
        return str_to_json(get_file(metadata_path))

    def get_thumbnail(self, title: str) -> bytes:
        thumbnail_path = self.path_manager.get_projects_path(title) / THUMBNAIL
        self.logger.debug(f"Retrieving thumbnail for project: {title}")
        return read_image_file(thumbnail_path)

    def delete_project(self, title: str) -> bool:
        project_path = self.path_manager.get_projects_path(title)
        success = delete_directory(project_path)
        if success:
            self.logger.info(f"Deleted project directory: {project_path}")
        else:
            self.logger.error(f"Failed to delete project directory: {project_path}")
        return success

    def rename_project(self, old_title: str, new_title: str):
        prev_project_path = self.path_manager.get_projects_path(old_title)
        rename_path(prev_project_path, new_title)
        self.logger.info(f"Renamed project from {old_title} to {new_title}")
