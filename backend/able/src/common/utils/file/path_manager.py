from pathlib import Path
from src.domain.block.enums import BlockType
from src.common.utils.file.constants import *

HOME_PATH = Path.home()
APPLICATION_NAME = "able"
VERSION = "v1"

class PathManager:

    BASE_PATH = HOME_PATH / APPLICATION_NAME / VERSION

    def __init__(self):
        self.blocks_path = self.BASE_PATH / "blocks"
        self.data_path = self.BASE_PATH / "data"
        self.deploy_path = self.data_path / "deploy"
        self.devices_path = self.data_path / "devices"
        self.projects_path = self.data_path / "projects"

    def get_deploy_path(self) -> Path:
        return self.deploy_path

    def get_devices_path(self) -> Path:
        return self.devices_path

    def get_device_path(self, device_name: str) -> Path:
        return self.devices_path / f"{device_name}.json"

    def get_block_path(self, block_type: BlockType) -> Path:
        """특정 블록 타입 경로"""
        return self.blocks_path / block_type.value

    def get_projects_path(self, name: str) -> Path:
        """프로젝트 경로"""
        return self.projects_path / name

    def get_block_graph_path(self, name: str) -> Path:
        """프로젝트 블록 그래프 파일 경로"""
        return self.get_projects_path(name) / BLOCK_GRAPH

    def get_train_results_path(self, name: str) -> Path:
        """학습 결과 목록 경로"""
        return self.get_projects_path(name) / TRAIN_RESULTS

    def get_train_result_path(self, name: str, result_name: str) -> Path:
        """학습 결과 경로"""
        return self.get_projects_path(name) / TRAIN_RESULTS / result_name

    def get_checkpoints_path(self, name:str, result_name: str):
        """에포크 목록 경로"""
        return self.get_train_result_path(name, result_name) / CHECKPOINTS

    def get_checkpoint_path(self, name: str, result_name: str, checkpoint: str) -> Path:
        """에포크별 경로"""
        return self.get_train_result_path(name, result_name) / CHECKPOINTS / checkpoint

    def get_feature_maps_path(self, name: str, result_name: str, checkpoint: str) -> Path:
        """특정 에포크의 피처맵 이미지 디렉터리 경로"""
        return self.get_checkpoint_path(name, result_name, checkpoint) / FEATURE_MAPS
