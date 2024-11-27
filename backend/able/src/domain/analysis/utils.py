import torch
import torch.nn as nn
import numpy as np
import cv2
import logging
import matplotlib.pyplot as plt
import torch.nn.functional as F
from PIL import Image
from typing import List
from pathlib import Path

from src.domain.train.utils import load_transform_pipeline
from src.domain.canvas.schemas import Canvas
from src.common.utils.file.utils import get_file, create_file
from src.common.utils.utils import str_to_json, json_to_str
from src.domain.analysis.exceptions import ModelLoadException
from src.domain.analysis.schemas import ClassScore, AnalysisResult
from src.domain.train.schemas import TrainResultMetadata
from src.common.utils.file.constants import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureMapExtractor:
    def __init__(self, model: nn.Module, project_name: str, result_name: str, result_path: Path, checkpoint_path: Path, feature_maps_path: Path, img_path: Path, device: str = 'cpu') -> None:
        self.project_name = project_name
        self.result_name = result_name
        self.result_path = result_path
        self.checkpoint_path = checkpoint_path
        self.device: str = device
        self.model: nn.Module = model

        self.feature_maps_path = feature_maps_path
        self.final_feature_map = None 
        self.output = None  
        self.heatmap_block_id : str = None

        self.img_path = img_path

    def analyze(self) -> AnalysisResult:
        self.build_model()
        self.model.eval()

        input_img = preprocess_image(self.project_name, self.result_name, self.img_path, self.device)
        input_img.requires_grad = True

        self.output = self.model(input_img)
        self.save_heatmap()
        scores = self.save_top_k_scores()
        return AnalysisResult(class_scores=scores, heatmap_block_id=self.heatmap_block_id.replace("module_list.", ""))
    
    def build_model(self):
        if self.model is None:
            logger.error(f"모델이 로드되지 않은 상태에서 훅 적용")
            raise ModelLoadException("모델이 로드되지 않았습니다.")

        last_conv_layer_name = None
        for name, module in self.model.module_list.named_modules():
            self.heatmap_block_id = name
            if isinstance(module, nn.Conv2d):
                last_conv_layer_name, last_module = name, module
                module.register_forward_hook(self.get_hook_fn(name))

        if last_conv_layer_name:
            last_module.register_forward_hook(self.get_final_layer_hook())

        self.model.to(self.device)

    def get_hook_fn(self, layer_name: str) -> callable:
        def hook_fn(module: nn.Module, input: torch.Tensor, output: torch.Tensor) -> None:
            self.save_feature_map(output.detach(), layer_name)
        return hook_fn
    
    def get_final_layer_hook(self):
        def hook_fn(module, input, output):
            self.final_feature_map = output
            self.final_feature_map.retain_grad()
        return hook_fn

    def save_feature_map(self, fmap: torch.Tensor, layer_name: str) -> None:
        fmap = fmap.mean(dim=1).squeeze().cpu().numpy()

        fmap = (fmap - fmap.min()) / (fmap.max() - fmap.min())

        plt.imshow(fmap, cmap='viridis', interpolation='nearest')
        plt.axis('off')
        plt.savefig(str(self.feature_maps_path / f"{layer_name}.jpg"), bbox_inches='tight', pad_inches=0.1)
        plt.close()

    def save_heatmap(self) -> None:
        if self.final_feature_map is None:
            raise ValueError("최종 피쳐 맵이 없습니다. 모델을 통해 이미지를 먼저 예측하세요.")
        if self.output is None:
            raise ValueError("출력값이 없습니다.")
    
        target_class = self.output.argmax(dim=1).item()
        self.model.zero_grad()
        self.output[0, target_class].backward()
    
        gradients = self.final_feature_map.grad[0] 
        weights = torch.mean(gradients, dim=(1, 2))  
    
        weighted_sum = torch.sum(self.final_feature_map[0] * weights.view(-1, 1, 1), dim=0)
        heatmap = weighted_sum.detach().cpu().numpy()
    
        heatmap = np.maximum(heatmap, 0)
        heatmap /= heatmap.max()
        heatmap = np.uint8(255 * heatmap) 
        heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    
        original_image = cv2.imread(str(self.img_path))
        heatmap_resized = cv2.resize(heatmap, (original_image.shape[1], original_image.shape[0]))

        overlay = heatmap_resized * 0.4 + original_image
        cv2.imwrite(str(self.checkpoint_path / HEATMAP), overlay)
    

    def save_top_k_scores(self, k: int = 3) -> List[ClassScore]:
        probabilities = F.softmax(self.output, dim=1)
        top_values, top_indices = probabilities.topk(k, dim=1)

        top_values = top_values[0].cpu().detach().numpy()
        top_indices = top_indices[0].cpu().detach().numpy()

        class_names = get_class_names(self.result_path / METADATA)
        logger.info(f"상위 {k}개의 클래스: {[class_names[idx] for idx in top_indices]}")
        logger.info(f"상위 {k}개의 클래스 점수 (확률): {top_values}")

        # 100점 만점으로 변환
        scores = [
            ClassScore(
                class_name=class_names[idx] if class_names else f"Class {idx}",
                class_score=round(float(score) * 100)  # float 변환 후 100점 만점 계산
            )
            for idx, score in zip(top_indices, top_values)
        ]
        create_file(self.checkpoint_path / ANALYSIS_RESULT, json_to_str(AnalysisResult(class_scores=scores, heatmap_block_id=self.heatmap_block_id.replace("module_list.", ""))))

        return scores


# json 파일을 읽고 블록 리스트를 반환
def read_blocks(path: Path) -> Canvas:
    return Canvas(**str_to_json(get_file(path)))

# 이미지 전처리
def preprocess_image(project_name: str, result_name: str, img_path: str, device: str = 'cpu') -> torch.Tensor:
    img = Image.open(img_path).convert('RGB')
    preprocess = load_transform_pipeline(project_name, result_name)
    return preprocess(img).unsqueeze(0).to(device)

# 모델 로드
def load_model(path: Path, device: str = 'cpu') -> nn.Module :
    try:
        model = torch.load(path, map_location=device)
        return model
    except Exception as e :
            logger.error(f"모델 로드 실패: {e}")
            raise ModelLoadException("모델 로드에 실패하였습니다.")

# 파라미터 로드
def load_parameter(model: nn.Module, path: str, device: str = 'cpu') :
    try:
        model.load_state_dict(torch.load(path, map_location=device), strict= False)
    except Exception as e:
        logger.error(f"파라미터 적용 실패: {e}")
        raise ModelLoadException("파라미터 적용에 실패하였습니다.")

def get_class_names(path: Path) -> list[str]:
        return TrainResultMetadata(**str_to_json(get_file(path))).classes
    
