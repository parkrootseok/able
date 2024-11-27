import json
from pathlib import Path

from math import ceil
from src.domain.deploy.enums import ApiStatus
from src.domain.deploy.schema.dto import ApiInformation
from src.common.utils.file.utils import get_file, create_file, remove_file, get_files
from src.common.utils.file.path_manager import PathManager
from src.common.utils.utils import str_to_json, json_to_str, handle_pagination


class DeployRepository:
    def __init__(self):
        self.path_manager = PathManager()
        self.METADATA_PATH = self.path_manager.deploy_path / "metadata.json"
        self.ROUTER_DIR_PATH = Path(__file__).resolve().parent.parent.parent.parent / "deploy_server/src/routers"

    # ------ Metadata Management ------
    def get_metadata(self) -> dict:
        if not self.METADATA_PATH.exists():
            default_metadata = {
                "api_version": "0.33.1",
                "port": "8088",
                "pid": None,
                "status": ApiStatus.STOP.value
            }
            create_file(self.METADATA_PATH, json.dumps(default_metadata))
        return str_to_json(get_file(self.METADATA_PATH))

    def update_metadata(self, data: dict) -> bool:
        return create_file(self.METADATA_PATH, json_to_str(data))

    # ------ Router Metadata Management ------
    def get_router_metadata(self, path_name: str) -> dict:
        metadata_path = self._get_router_metadata_path(path_name)
        return str_to_json(get_file(metadata_path))

    def create_router_metadata(self, path_name: str, data: dict) -> bool:
        metadata_path = self._get_router_metadata_path(path_name)
        return create_file(metadata_path, json_to_str(data))

    def update_router_metadata(self, path_name: str, status: ApiStatus) -> bool:
        metadata_path = self._get_router_metadata_path(path_name)
        metadata = self.get_router_metadata(path_name)
        metadata["status"] = status.value
        return create_file(metadata_path, json_to_str(metadata))

    def delete_router_metadata(self, path_name: str) -> bool:
        file_path = self._get_router_metadata_path(path_name)
        return remove_file(file_path)

    # ------ Router File Management ------
    def create_router(self, path_name: str, content: str) -> bool:
        file_path = self._get_router_path(path_name)
        return create_file(file_path, content)

    def delete_router(self, path_name: str) -> bool:
        file_path = self._get_router_path(path_name)
        return remove_file(file_path)

    def exists_router(self, path_name: str) -> bool:
        file_path = self._get_router_path(path_name)

        if file_path.exists():
            return True

        return False

    # ------ API List Retrieval ------
    def get_apis(self, page: int, page_size: int) -> tuple[int, list[ApiInformation]]:
        api_files = [f for f in get_files(self.path_manager.deploy_path) if f != 'metadata.json']
        total_size = len(api_files)

        if total_size == 0:
            return 0, []

        total_pages = ceil(total_size / page_size)
        paginated_files = handle_pagination(api_files, page, page_size)
        return total_pages, [ApiInformation(**str_to_json(get_file(self.path_manager.deploy_path / api))) for api in paginated_files]

    # ------ Helper Methods ------
    def _get_router_metadata_path(self, path_name: str) -> Path:
        return self.path_manager.get_deploy_path() / f"{path_name}.json"

    def _get_router_path(self, path_name: str):
        return self.ROUTER_DIR_PATH / f"{path_name}.py"