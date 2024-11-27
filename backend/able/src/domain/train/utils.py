from collections import defaultdict, deque

import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms
from torch.utils.data.dataloader import DataLoader
from torch.utils.data import random_split, Dataset, Subset
from typing import Iterator, Any

from src.domain.block.enums import BlockType, ArgType
from torchvision.datasets import ImageFolder
from torchvision.transforms import Compose

from src.domain.block.schemas import Block, Arg
from src.domain.block.utils import convert_block_to_obj
from src.domain.canvas.schemas import Edge, CanvasBlock, Canvas
from src.domain.train.enums import TrainStatus

from src.domain.train.schemas import TrainResultMetrics, TrainResultMetadata, PerformanceMetrics, HyperParameter, SaveHyperParameter

from src.common.utils.file.utils import create_file, get_file
from src.common.utils.file.path_manager import PathManager
from src.common.utils.utils import json_to_str, str_to_json
from datetime import datetime

from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns

from src.common.utils.file.constants import *

import pickle

MAX_LOSS = 10e8

path_manager = PathManager()


class TrainLogger:
    def __init__(self, project_name: str, result_name: str = datetime.now().strftime("%Y%m%d_%H%M%S")):
        self.project_name = project_name
        self.result_name = result_name

        # 기존 경로 생성 로직 제거, 결과 및 에포크 디렉터리는 서비스에서 생성
        self.result_path = path_manager.get_train_result_path(self.project_name, self.result_name)

        self.metadata_path = self.result_path / METADATA

    def update_status(self, status: TrainStatus) -> None:
        metadata_content = get_file(self.metadata_path)
        metadata_dict = str_to_json(metadata_content)

        metadata_dict["status"] = status.value

        new_metadata_content = json_to_str(metadata_dict)
        create_file(self.metadata_path, new_metadata_content)

    def create_epoch_log(self, checkpoint: str, accuracy: float, validation_loss: float, training_loss: float):
        epoch_path = path_manager.get_checkpoint_path(self.project_name, self.result_name, checkpoint)

        create_file(epoch_path / ACCURACY, json_to_str({'accuracy': accuracy}))
        create_file(epoch_path / VALIDATION_LOSS, json_to_str({'loss': validation_loss}))
        create_file(epoch_path / TRAINING_LOSS, json_to_str({'loss': training_loss}))

    def save_train_result(self, metrics: TrainResultMetrics):
        # 성능 지표 저장 (performance_metrics.json)
        # 성능 지표 저장 (performance_metrics.json)
        performance_metrics_data = metrics.performance_metrics.model_dump()
        create_file(self.result_path / PERFORMANCE_METRICS, json_to_str({"metrics": performance_metrics_data}))

        # F1 스코어 저장 (f1_score.json)
        create_file(self.result_path / F1_SCORE, json_to_str({"f1_score": metrics.f1}))

        # 혼동 행렬 저장 (confusion_matrix.jpg)
        confusion_matrix_path = self.result_path / CONFUSION_METRICS
        metrics.confusion_matrix.savefig(confusion_matrix_path, format="jpg")

    def save_model(self, model: nn.Module, file_name: str):
        torch.save(model, f"{self.result_path}/{file_name}")

class Trainer:
    """모델의 학습을 책임지는 클래스
    """
    def __init__(self, model: nn.Module, dataset: ImageFolder, criterion: nn.Module, optimizer: optim.Optimizer, batch_size, logger: TrainLogger, checkpoint_interval: int = 10, device: str = 'cpu'):
        self.model = model.to(device)
        self.dataset = dataset
        self.train_data_loader, self.valid_data_loader, self.test_data_loader = [create_data_loader(dataset_split, batch_size) for dataset_split in split_dataset(dataset)]
        self.criterion = criterion
        self.optimizer = optimizer
        self.logger = logger
        self.checkpoint_interval = checkpoint_interval
        self.device = device

    def train_epoch(self) -> float:
        self.model.train()  # 모델을 훈련 모드로 전환
        running_loss = 0.0

        for inputs, targets in self.train_data_loader:
            inputs, targets = inputs.to(self.device), targets.to(self.device)

            # Gradients 초기화
            self.optimizer.zero_grad()

            # Forward pass
            outputs = self.model(inputs)

            loss = self.criterion(outputs, targets)

            # Backward pass and optimize
            loss.backward()
            self.optimizer.step()

            running_loss += loss.item()

        epoch_loss = running_loss / len(self.train_data_loader)

        return epoch_loss

    def validate(self) -> tuple[float, float]:
        self.model.eval()  # 모델을 평가 모드로 전환
        running_loss = 0.0

        correct = 0
        total = 0

        with torch.no_grad():  # 평가 시에는 gradients가 필요 없으므로
            for inputs, targets in self.valid_data_loader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)

                outputs = self.model(inputs)

                _, predicted = torch.max(outputs, 1)  # 예측값 얻기
                correct += (predicted == targets).sum().item()  # 맞춘 샘플 수 누적
                total += targets.size(0)  # 전체 샘플 수 누적

                loss = self.criterion(outputs, targets)

                running_loss += loss.item()

        epoch_loss = running_loss / len(self.valid_data_loader)
        return correct / total, epoch_loss # valid accuracy, loss 반환

    def epoch_accuracy(self) -> float:
        self.model.eval()  # 모델을 평가 모드로 전환

        correct = 0  # 정확하게 예측한 샘플 수
        total = 0  # 전체 샘플 수

        with torch.no_grad():  # 평가 시에는 gradients가 필요 없으므로
            for inputs, targets in self.train_data_loader:
                inputs, targets = inputs.to(self.device), targets.to(self.device)

                outputs = self.model(inputs)

                _, predicted = torch.max(outputs, 1)  # 예측값 얻기
                correct += (predicted == targets).sum().item()  # 맞춘 샘플 수 누적
                total += targets.size(0)  # 전체 샘플 수 누적

        return correct / total # train accuracy 반환

    def train(self, epochs) -> None:
        best_train_loss = MAX_LOSS
        best_valid_loss = MAX_LOSS

        train_loss = 0
        train_accuracy = 0
        valid_loss = 0
        valid_accuracy = 0

        for epoch in range(epochs):

            # Training and validation
            train_loss = self.train_epoch()
            train_accuracy = self.epoch_accuracy()
            valid_accuracy, valid_loss = self.validate()

            # Checkpoint (간단히 마지막 모델만 저장)
            if (epoch + 1) % self.checkpoint_interval == 0:
                self.logger.create_epoch_log(f"epoch_{epoch + 1}", train_accuracy, train_loss, valid_loss)
                self.logger.save_model(self.model, f"{CHECKPOINTS}/epoch_{epoch + 1}/{MODEL}")

            if best_train_loss > train_loss:
                self.logger.create_epoch_log(TRAIN_BEST, train_accuracy, train_loss, valid_loss)
                self.logger.save_model(self.model, f"{CHECKPOINTS}/{TRAIN_BEST}/{MODEL}")
                best_train_loss = train_loss

            if best_valid_loss > valid_loss:
                self.logger.create_epoch_log(VALID_BEST, train_accuracy, train_loss, valid_loss)
                self.logger.save_model(self.model, f"{CHECKPOINTS}/{VALID_BEST}/{MODEL}")
                best_valid_loss = valid_loss

        self.logger.create_epoch_log(FINAL, train_accuracy, train_loss, valid_loss)
        self.logger.save_model(self.model, f"{CHECKPOINTS}/{FINAL}/{MODEL}")

    def test(self) -> None:
        self.model.eval()  # 평가 모드로 전환 (드롭아웃 비활성화 등)

        y_true = []
        y_pred = []

        top1_correct = 0
        top5_correct = 0
        total = 0

        with torch.no_grad():  # 그래디언트 비활성화로 메모리 절약
            for inputs, labels in self.test_data_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self.model(inputs)
                _, predicted = torch.max(outputs, 1)

                # Top-1 예측값
                y_true.extend(labels.cpu().numpy())
                y_pred.extend(predicted.cpu().numpy())
                top1_correct += (predicted == labels).sum().item()  # Top-1 정답 카운트
                total += labels.size(0)

                # Top-5 예측값
                _, top5_pred = outputs.topk(5, dim=1)  # 각 샘플에 대해 상위 5개 예측
                labels = labels.view(-1, 1)  # (batch_size, 1)로 변환
                top5_correct += (top5_pred == labels).sum().item()  # Top-5 정답 카운트

        # 정밀도 계산
        precision = precision_score(y_true, y_pred, average='macro', zero_division=0)

        # 재현율 계산
        recall = recall_score(y_true, y_pred, average='macro', zero_division=0)

        # F1-스코어 계산
        f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)

        # 혼동 행렬 계산
        fig = plot_confusion_matrix(y_true, y_pred, self.dataset.classes)

        # Top-1 및 Top-5 정확도 계산
        top1_accuracy = top1_correct / total
        top5_accuracy = top5_correct / total

        # 성능 지표 객체 생성
        performance_metrics = PerformanceMetrics(
            accuracy=top1_accuracy,
            top5_accuracy=top5_accuracy,
            precision=precision,
            recall=recall
        )

        # TrainResultMetrics 객체 생성
        metrics = TrainResultMetrics(
            performance_metrics=performance_metrics,
            f1=f1,
            confusion_matrix=fig  # confusion_matrix에 Figure 객체 전달
        )

        # 성능 결과 저장
        self.logger.save_train_result(metrics)

def plot_confusion_matrix(y_true, y_pred, class_names) -> Figure:
    plt.ioff()
    # 혼동 행렬 계산
    conf_matrix = confusion_matrix(y_true, y_pred)

    # 플롯 크기 및 스타일 설정
    fig, ax = plt.subplots()
    sns.heatmap(conf_matrix, ax=ax, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names)

    # 제목 및 축 레이블 설정
    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Predicted Labels")
    ax.set_ylabel("True Labels")
    plt.xticks(rotation=45)
    plt.yticks(rotation=45)
    fig.tight_layout()

    return fig

def create_dataset(data_path: str, train_transform:Compose) -> ImageFolder:
    return ImageFolder(data_path, transform=train_transform)

def create_data_loader(dataset: Dataset, batch_size: int) -> DataLoader:
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)

def split_dataset(dataset: Dataset) -> list[Subset[Any]]:
    return random_split(dataset, [0.6, 0.2, 0.2])

def create_data_preprocessor(transform_blocks: list[CanvasBlock]) -> Compose:
    return Compose([convert_block_to_obj(transform_block) for transform_block in transform_blocks])

def convert_layer_block_to_module(layer_block: CanvasBlock) -> nn.Module | None:

    if layer_block.type != BlockType.LAYER:
        return None

    return convert_block_to_obj(layer_block)

def convert_activation_block_to_module(activation_block: CanvasBlock) -> nn.Module | None:
    torchvision.transforms.Resize()
    if activation_block.type != BlockType.ACTIVATION:
        return None

    return convert_block_to_obj(activation_block)

def convert_criterion_block_to_module(loss_block: CanvasBlock) -> nn.Module | None:

    if loss_block.type != BlockType.LOSS:
        return None

    return convert_block_to_obj(loss_block)

def convert_optimizer_block_to_optimizer(optimizer_block: CanvasBlock, parameters: Iterator[nn.Parameter]) -> optim.Optimizer | None:

    if optimizer_block.type != BlockType.OPTIMIZER:
        return None

    optimizer_block.args.append(Arg(name="params", value=parameters, is_required=True, type=ArgType.MODEL_PARAMS))

    return convert_block_to_obj(optimizer_block)

def convert_operation_block_to_module(operation_block: CanvasBlock) -> nn.Module | None:

    if operation_block.type != BlockType.OPERATION:
        return None

    return convert_block_to_obj(operation_block)

def topological_sort(blocks: list[CanvasBlock], edges: list[Edge]) -> list[CanvasBlock]:
    graph = defaultdict(list)
    in_degree = {block.id: 0 for block in blocks}

    for edge in edges:
        graph[edge.source].append(edge.target)
        in_degree[edge.target] += 1

    queue = deque([block for block in blocks if in_degree[block.id] == 0])
    sorted_blocks = []

    while queue:
        block = queue.popleft()
        sorted_blocks.append(block)

        for neighbor in graph[block.id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(next(b for b in blocks if b.id == neighbor))

    if len(sorted_blocks) != len(blocks):
        raise ValueError("Cycle detected in the graph; topological sort not possible.")

    return list(sorted_blocks)

class UserModel(nn.Module):
    def __init__(self, blocks: list[CanvasBlock], edges: list[Edge]):
        super(UserModel, self).__init__()
        self.child_map = defaultdict(list)
        self.module_list = nn.ModuleList()
        self.module_id_list = []

        for block in blocks:
            module = convert_block_to_obj(block)

            self.module_list.add_module(block.id, module)
            self.module_id_list.append(block.id)

        for edge in edges:
            self.child_map[edge.source].append(edge.target)

    def forward(self, x):
        layer_input: dict[str, list] = defaultdict(list)
        layer_input[self.module_id_list[0]].append(x)

        output = 0
        for module_id in self.module_id_list:
            submodule = self.module_list.get_submodule(module_id)
            in_data = layer_input.pop(module_id)

            output = submodule(*in_data)

            for child_id in self.child_map[module_id]:
                layer_input[child_id].append(output)

        return output

def convert_block_graph_to_model(blocks: list[CanvasBlock], edges: list[Edge]) -> nn.Module | None:
    sorted_blocks = topological_sort(blocks, edges)

    model = UserModel(sorted_blocks, edges)

    return model

def split_blocks(blocks: list[Block]) -> tuple[
    Block | None, list[Block], list[Block], list[Block], list[Block]
]:

    data_block = None
    transform_blocks, loss_blocks, optimizer_blocks, others = [], [], [], []

    for block in blocks:
        match block.type:
            case BlockType.DATA:
                if data_block is None:
                    data_block = block
                else:
                    raise ValueError("Multiple data blocks found. Expected only one.")
            case BlockType.TRANSFORM:
                transform_blocks.append(block)
            case BlockType.LOSS:
                loss_blocks.append(block)
            case BlockType.OPTIMIZER:
                optimizer_blocks.append(block)
            case _:
                others.append(block)

    return data_block, transform_blocks, loss_blocks, optimizer_blocks, others

def filter_blocks_connected_to_data(
        blocks: list[CanvasBlock],
        edges: list[Edge]
) -> list[CanvasBlock] | None:
    """
    그래프의 루트인 데이터 블록과 연결된 블록들만 반환하는 함수
    """
    data_block = None
    for block in blocks:
        if block.type == BlockType.DATA:
            data_block = block
            break

    if data_block is None:
        return None

    adj_dict = defaultdict(list)

    for edge in edges:
        adj_dict[edge.source].append(edge.target)

    q = deque()
    q.append(data_block.id)

    conn_block_id_set = set()
    conn_block_id_set.add(data_block.id)

    while q:
        cur_id = q.popleft()

        for next_id in adj_dict[cur_id]:
            q.append(next_id)
            conn_block_id_set.add(next_id)

    return [block for block in blocks if block.id in conn_block_id_set]

def filter_edges_from_block_connected_data(blocks: list[Block], edges: list[Edge]) -> list[Edge]:
    block_id = set(block.id for block in blocks)

    return [edge for edge in edges if edge.source in block_id]

def save_result_block_graph(project_name: str, result: str, blocks: list[CanvasBlock], edges: list[Edge]):

    block_graph_path = path_manager.get_train_result_path(project_name, result) / BLOCK_GRAPH
    if create_file(block_graph_path, Canvas(blocks=blocks, edges=edges).model_dump_json()):
        return True

    raise

def convert_canvas_blocks(blocks: list[Block]) -> list[CanvasBlock]:
    return [block for block in blocks if isinstance(block, CanvasBlock)]

def save_result_model(project_name: str, result: str, model: nn.Module):
    torch.save(model, str(path_manager.get_train_results_path(project_name) / result / MODEL))

def save_result_hyper_parameter(project_name: str, result: str, batch_size: int, epoch: int):

    hyper_parameter_path = path_manager.get_train_results_path(project_name) / result / HYPER_PARAMETER

    if create_file(hyper_parameter_path, json_to_str(SaveHyperParameter(hyper_parameter=HyperParameter(batch_size=batch_size, epoch=epoch)))):
        return True

    raise

def find_argument(data_block: CanvasBlock, arg_name: str):
    """CanvasBlock 의 특정 arg_name 값 반환"""
    for arg in data_block.args:
        if arg.name == arg_name:
            return arg.value
    return None

def save_metadata(project_name: str, result_name: str, data_block: CanvasBlock, classes: list[str]) -> None:

    # 메타데이터 정보 추출
    data_path = find_argument(data_block, "data_path")
    # input_shape = find_argument(data_block, "input_shape")
    # classes = find_argument(data_block, "classes")

    # 데이터 검증
    if not all([data_path, classes]):
        raise ValueError("메타데이터 정보가 올바르지 않습니다.")

    # 메타데이터 저장
    metadata = TrainResultMetadata(
        data_path=data_path,
        # input_shape=input_shape,
        classes=classes,
        status=TrainStatus.RUNNING
    )

    metadata_path = path_manager.get_train_result_path(project_name, result_name) / METADATA

    create_file(metadata_path, json_to_str(metadata.model_dump()))

def find_data_path(data_block: CanvasBlock):
    for arg in data_block.args:
        if arg.name == "data_path":
            return arg.value
    return None

def filter_model_edge(model_blocks: list[CanvasBlock], edges: list[Edge]) -> list[Edge]:
    model_block_set = set(block.id for block in model_blocks)

    return [edge for edge in edges if edge.source in model_block_set and edge.target in model_block_set]

def save_transform_pipeline(project_name: str, result_name:str, transform_pipeline: torchvision.transforms.Compose) -> None:
    result_path = path_manager.get_train_result_path(project_name, result_name)

    with open(result_path / TRANSFORM_PIPELINE, 'wb') as f:
        pickle.dump(transform_pipeline, f, pickle.HIGHEST_PROTOCOL)

def load_transform_pipeline(project_name: str, result_name:str) -> torchvision.transforms.Compose | None:
    result_path = path_manager.get_train_result_path(project_name, result_name)

    transform_pipeline_path = result_path / TRANSFORM_PIPELINE
    if not transform_pipeline_path.exists():
        return None

    with open(transform_pipeline_path, 'rb') as f:
        return pickle.load(f)

if __name__=="__main__":
    print(torchvision.models.resnet18())