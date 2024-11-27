import logging

from fastapi import UploadFile
from src.common.utils.logger.utils import get_logger
from src.common.utils.file.path_manager import PathManager
from src.common.utils.file.utils import read_image_file, save_img, create_directory, get_file
from src.common.utils.utils import encode_image_to_base64, str_to_json
from src.domain.analysis.utils import FeatureMapExtractor, load_model
from src.domain.canvas.schemas import Canvas
from src.domain.analysis.schemas import *
from src.common.utils.file.constants import *

logger = get_logger(__name__, level=logging.DEBUG)
pathManager = PathManager()


def get_feature_map(request: FeatureMapRequest) -> str:
    feature_map_path = pathManager.get_feature_maps_path(request.project_name, request.result_name, request.epoch_name)

    image_name = request.block_id + ".jpg"
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

    create_directory(feature_maps_path)
    img_path = await save_img(checkpoint_path, ORIGINAL, file)

    device = 'cpu'
    if device_index != -1:
        device = f"cuda:{device_index}"

    model_path = checkpoint_path / MODEL
    model = load_model(model_path, device)

    extractor = FeatureMapExtractor(model, project_name, result_name, result_path, checkpoint_path, feature_maps_path, img_path, device)
    result = extractor.analyze()

    heatmap_img = encode_image_to_base64(read_image_file(checkpoint_path / HEATMAP))
    return AnalyzeResponse(image=heatmap_img, class_scores=result.class_scores, heatmap_block_id=result.heatmap_block_id)

def get_block_graph(project_name: str, result_name: str) -> Canvas :
    block_graph_path = pathManager.get_train_result_path(project_name, result_name) / BLOCK_GRAPH
    block = Canvas(**str_to_json(get_file(block_graph_path)))
    return block


def get_heatmap(project_name: str, result_name:str, checkpoint_name:str) -> Optional[HeatMapResponse]:
    checkpoint_path = pathManager.get_checkpoint_path(project_name, result_name, checkpoint_name)
    try: 
        heatmap = encode_image_to_base64(read_image_file(checkpoint_path / HEATMAP))
        original = encode_image_to_base64(read_image_file(checkpoint_path / ORIGINAL))
        analysis_result = AnalysisResult(**str_to_json(get_file(checkpoint_path / ANALYSIS_RESULT)))
    except Exception as e:
        logger.info(f"이전에 진행된 분석 결과가 없음: {e}")
        return None
    
    return HeatMapResponse(original_img=original, heatmap_img=heatmap, class_scores=analysis_result.class_scores, heatmap_block_id=analysis_result.heatmap_block_id )
