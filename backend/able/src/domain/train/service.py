import gc
import json
import logging

from . import TrainRequest
from src.domain.train.schemas import TrainResultResponse, EpochResult, Loss, Accuracy
from .utils import *
from src.common.utils.file.path_manager import PathManager
from src.common.utils.file.utils import get_file, create_directory
from src.common.utils.utils import encode_image_to_base64
from src.common.utils.file.utils import read_image_file
from src.common.utils.logger.utils import get_logger
from typing import List

from src.domain.train_log.utils import format_float
from ..device.schema import DeviceStatus
from ..device.utils import get_device_status, update_device_status
from src.common.utils.file.constants import *

import time

logger = get_logger(__name__, level=logging.DEBUG)
path_manager = PathManager()

def train_in_background(request: TrainRequest):
    logger.debug("학습 시작[epoch: %s, batch size: %s]", request.epoch, request.batch_size)
    train(request)
    logger.debug("학습 종료")

def train(request: TrainRequest):

    blocks_connected_to_data = filter_blocks_connected_to_data(request.canvas.blocks, request.canvas.edges)

    if blocks_connected_to_data is None:
        raise Exception("유효하지 않은 그래프")

    data_block, transform_blocks, loss_blocks, optimizer_blocks, model_blocks = split_blocks(blocks_connected_to_data)

    if data_block is None:
        raise ValueError("Data block is required but was not found.")

    if isinstance(data_block, CanvasBlock):
        data_block: CanvasBlock = data_block

    data_path = find_data_path(data_block)

    # 학습에서 사용하는 간선 추출
    edges = filter_edges_from_block_connected_data(blocks_connected_to_data, request.canvas.edges)

    model_blocks = [block for block in model_blocks if isinstance(block, CanvasBlock)]
    edges_model = filter_model_edge(model_blocks, edges)

    model = convert_block_graph_to_model(model_blocks, edges_model)

    if model is None:
        raise Exception()

    # 손실함수 블록 변환
    criterion = convert_criterion_block_to_module(loss_blocks[0])

    if criterion is None:
        raise Exception("손실함수가 없습니다.")

    # 최적화 블록 변환
    optimizer = convert_optimizer_block_to_optimizer(optimizer_blocks[0], model.parameters())

    if optimizer is None:
        raise Exception("최적화 모듈이 없습니다.")

    # TrainLogger 초기화 전 디렉터리 생성
    project_name = request.project_name
    result_name = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 결과 및 에포크 디렉터리 생성
    result_path = path_manager.get_train_results_path(project_name) / result_name
    epochs_path = path_manager.get_checkpoints_path(project_name, result_name)
    create_directory(result_path)
    create_directory(epochs_path)

    # 전처리 파이프라인 블록 변환
    transform_pipeline = create_data_preprocessor(transform_blocks)

    # 전처리 파이프라인 저장
    save_transform_pipeline(project_name, result_name, transform_pipeline)

    # 데이터셋 가져오기
    dataset = create_dataset(data_path, transform_pipeline)

    # 데이터셋 메타데이터 저장
    save_metadata(project_name, result_name, data_block, dataset.classes)

    # 학습 모델 그래프 저장
    save_result_block_graph(request.project_name, result_name, blocks_connected_to_data, edges)

    # 하이퍼 파라미터 정보 저장 (hyper_parameters.json)
    save_result_hyper_parameter(request.project_name, result_name, request.batch_size, request.epoch)

    device = 'cpu'
    if request.device.index != -1:
        device = f"cuda:{request.device.index}"

    if get_device_status(request.device.name) == DeviceStatus.IN_USE:
        raise Exception()

    update_device_status(request.device.name, DeviceStatus.IN_USE)

    train_logger = TrainLogger(project_name, result_name)

    try:

        trainer = Trainer(model, dataset, criterion, optimizer, request.batch_size, train_logger, device=device)

        trainer.train(request.epoch)

        logger.debug("테스트 시작")
        trainer.test()
        logger.debug("테스트 종료")

        train_logger.update_status(TrainStatus.COMPLETE)
    except Exception as e:
        train_logger.update_status(TrainStatus.FAIL)
        raise e
    finally:
        torch.cuda.memory.empty_cache()
        gc.collect()
        update_device_status(request.device.name, DeviceStatus.NOT_IN_USE)

def load_train_result(project_name: str, result_name: str) -> TrainResultResponse:

    # 결과 디렉터리 경로 설정
    result_path = path_manager.get_train_result_path(project_name, result_name)

    # 혼동 행렬 이미지 로드 및 인코딩
    image_bytes = read_image_file(result_path / CONFUSION_METRICS)  # 파일 경로에서 bytes 읽기
    confusion_matrix = encode_image_to_base64(image_bytes)

    # 성능 지표 로드
    performance_metrics_data = json.loads(get_file(result_path / PERFORMANCE_METRICS))
    performance_metrics = PerformanceMetrics.model_validate(performance_metrics_data["metrics"])

    # F1 스코어 로드
    f1_score = format_float(str_to_json(get_file(result_path / F1_SCORE))["f1_score"])

    # 에포크 결과 로드
    epochs_path = path_manager.get_checkpoints_path(project_name, result_name)
    epoch_results: List[EpochResult] = []

    for epoch_dir in epochs_path.iterdir():
        if epoch_dir.is_dir():
            epoch_id = epoch_dir.name

            training_loss_data = str_to_json(get_file(epoch_dir / TRAINING_LOSS))
            validation_loss_data = str_to_json(get_file(epoch_dir / VALIDATION_LOSS))
            accuracy_data = str_to_json(get_file(epoch_dir / ACCURACY))

            # 각 파일을 로드하여 모델 인스턴스로 변환
            training_loss = Loss(training=training_loss_data["loss"], validation=validation_loss_data["loss"])
            # validation_loss = Loss.model_validate(validation_loss_data)
            accuracy = Accuracy(accuracy=accuracy_data["accuracy"])

            # 에포크 결과 인스턴스 생성
            epoch_result = EpochResult(
                epoch=epoch_id,
                losses=training_loss,
                accuracies=accuracy
            )
            epoch_results.append(epoch_result)

    epochs = [epoch for epoch in epoch_results if epoch.epoch not in ("train_best", "valid_best", "final")]
    epochs.sort(key=lambda x : (len(x.epoch), x.epoch))
    epochs.extend([epoch for epoch in epoch_results if epoch.epoch in ("train_best", "valid_best", "final")])

    # TrainResultResponse 반환
    return TrainResultResponse(
        confusion_matrix=confusion_matrix,
        performance_metrics=performance_metrics,
        f1_score=str(f1_score),
        epoch_result=epochs
    )