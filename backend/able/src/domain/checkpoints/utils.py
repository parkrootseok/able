from src.common.utils.file.path_manager import PathManager
from src.common.utils.file.utils import get_directory
from src.common.utils.file.constants import *

pathManager = PathManager()

def sort_checkpoints(checkpoints: list[str]) -> list[str]:
    return sorted(checkpoints, key=lambda x: int(x.split('_')[1]))

def get_checkpoints(project_name: str, result_name: str, keyword: str = None) -> list[str]:
    checkpoints_path = pathManager.get_checkpoints_path(project_name, result_name)
    checkpoints = get_directory(checkpoints_path)
    if keyword is None:
        return [checkpoint.name for checkpoint in checkpoints if checkpoint.name not in {TRAIN_BEST, VALID_BEST, FINAL}]
    else:
        return [checkpoint.name for checkpoint in checkpoints if keyword in checkpoint.name and checkpoint.name not in {TRAIN_BEST, VALID_BEST, FINAL}]