import logging

from src.domain.checkpoints.schemas import CheckpointListResponse, CheckpointsPaginatedResponse
from src.common.utils.logger.utils import get_logger
from src.common.utils.file.path_manager import PathManager
from src.common.utils.file.utils import get_directory
from src.common.utils.file.constants import *
from src.common.utils import handle_pagination, has_next_page
from src.domain.checkpoints.utils import sort_checkpoints, get_checkpoints

logger = get_logger(__name__)
pathManager = PathManager()

def get_all_checkpoints(project_name: str, result_name: str) -> CheckpointListResponse:
    checkpoints = get_checkpoints(project_name, result_name)
    checkpoints = [TRAIN_BEST, VALID_BEST, FINAL] + checkpoints
    result = CheckpointListResponse(checkpoints=checkpoints)
    return result

def get_paginated_checkpoints(project_name: str, result_name: str, index: int, size: int) -> CheckpointsPaginatedResponse:
    checkpoints = sort_checkpoints(get_checkpoints(project_name, result_name))
    page_item = handle_pagination(checkpoints, index, size)
    return CheckpointsPaginatedResponse(checkpoints=page_item, has_next=has_next_page(len(checkpoints), index, size))

def search_checkpoint(project_name: str, result_name:str, keyword: str, index: int, size: int) -> CheckpointsPaginatedResponse:
    checkpoints = sort_checkpoints(get_checkpoints(project_name=project_name, result_name=result_name, keyword=keyword))
    page_item = handle_pagination(checkpoints, index, size)
    return CheckpointsPaginatedResponse(checkpoints=page_item, has_next=has_next_page(len(checkpoints), index, size))