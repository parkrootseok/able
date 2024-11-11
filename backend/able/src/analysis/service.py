import logging

from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile

from src.file.path_manager import PathManager
from src.file.utils import get_directory, read_image_file, save_img, create_directory, get_file
from src.utils import encode_image_to_base64, str_to_json, handle_pagination, has_next_page
from src.analysis.utils import FeatureMapExtractor, read_blocks, load_model
from src.train.utils import split_blocks
from src.canvas.schemas import Canvas
from src.analysis.schemas import *
from src.file.constants import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pathManager = PathManager()

def get_checkpoints(project_name: str, result_name: str, index: int, size: int) -> CheckpointResponse:
    checkpoints_path = pathManager.get_checkpoints_path(project_name, result_name)
    checkpoints = get_directory(checkpoints_path)
    items = [epoch.name for epoch in checkpoints if epoch.is_dir() and epoch.name not in {TRAIN_BEST, VALID_BEST, FINAL}]

    page_item = handle_pagination(items, index, size)

    return CheckpointResponse(epochs=page_item, has_next=has_next_page(len(items), index, size))


def get_feature_map(request: FeatureMapRequest) -> str:
    feature_map_path = pathManager.get_feature_maps_path(request.project_name, request.result_name, request.epoch_name)

    image_name = 'layers.' + request.block_id + ".jpg"
    image_data = None
    try:
        image_data = encode_image_to_base64(read_image_file(feature_map_path / image_name))
    except Exception as e:
        logger.error(f"feature map이 존재하지 않는 블록: {id}")

    return image_data

async def analyze(project_name: str, result_name: str, checkpoint_name:str, device_index: int, file: UploadFile) -> AnalyzeResponse:
    result_path = pathManager.get_train_result_path(project_name, result_name)
    checkpoint_path = pathManager.get_checkpoint_path(project_name, result_name, checkpoint_name)
    feature_maps_path = checkpoint_path / "feature_maps"

    block_graph_path = pathManager.get_train_result_path(project_name, result_name) / BLOCK_GRAPH
    block_graph = read_blocks(block_graph_path)

    _, transform_blocks, _, _, _ = split_blocks(block_graph.blocks)

    create_directory(feature_maps_path)
    img_path = await save_img(checkpoint_path, ORIGINAL, file)

    device = 'cpu'
    if device_index != -1:
        device = f"cuda:{device_index}"

    model_path = checkpoint_path / MODEL
    model = load_model(model_path, device)

    extractor = FeatureMapExtractor(model,result_path, checkpoint_path, feature_maps_path, transform_blocks, img_path, device)
    scores = extractor.analyze()

    heatmap_img = encode_image_to_base64(read_image_file(checkpoint_path / HEATMAP))
    return AnalyzeResponse(image=heatmap_img, class_scores=scores)

def get_block_graph(project_name: str, result_name: str) -> Canvas :
    block_graph_path = pathManager.get_train_result_path(project_name, result_name) / BLOCK_GRAPH
    block = Canvas(**str_to_json(get_file(block_graph_path)))
    return block


def get_heatmap(project_name: str, result_name:str, checkpoint_name:str) -> Optional[HeatMapResponse]:
    checkpoint_path = pathManager.get_checkpoint_path(project_name, result_name, checkpoint_name)
    try: 
        heatmap = encode_image_to_base64(read_image_file(checkpoint_path / HEATMAP))
        original = encode_image_to_base64(read_image_file(checkpoint_path / ORIGINAL))
        class_scores = ClassScores(**str_to_json(get_file(checkpoint_path / ANALYSIS_RESULT)))
    except Exception as e:
        logger.info(f"이전에 진행된 분석 결과가 없음: {e}")
        return None
    
    return HeatMapResponse(original_img=original, heatmap_img=heatmap, class_scores=class_scores.class_scores)
