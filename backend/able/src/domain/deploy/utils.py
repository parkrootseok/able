from src.domain.deploy.schema.request import RegisterApiRequest

def generate_include_statement(path_name: str) -> str:
    return f'from deploy_server.src.routers.{path_name} import router as {path_name}_router\napp.include_router({path_name}_router)\n'

def format_path_name(uri: str) -> str:
    return uri.strip("/").replace("/", "_")

def generate_router_content(request: RegisterApiRequest) -> str:
    return f"""
import torch
import io

from PIL import Image
from fastapi import APIRouter, UploadFile, File
from deploy_server.src.schemas import InferenceResponse
from src.common.utils.file.path_manager import PathManager
from src.common.utils.file.utils import get_file
from src.common.utils.file.constants import METADATA, MODEL
from src.common.utils.response.utils import ok
from src.domain.train.schemas import TrainResultMetadata
from src.common.utils import str_to_json

from src.domain.train.utils import load_transform_pipeline

router = APIRouter()
path_manager = PathManager()

@router.post("{request.uri}")
async def path_name_route(file: UploadFile = File(...)):

    project_name = "{request.project_name}"
    train_result = "{request.train_result}"
    checkpoint = "{request.checkpoint}"

    train_result_metadata_path = path_manager.get_train_result_path(project_name, train_result) / METADATA
    metadata = TrainResultMetadata(**str_to_json(get_file(train_result_metadata_path)))

    # base64를 이미지로 변환 
    image = await file.read()
    image = Image.open(io.BytesIO(image))

    # 전처리 파이프라인 가져오기
    transform_pipeline = load_transform_pipeline(project_name, train_result)

    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

    image: torch.Tensor = transform_pipeline(image)
    image = image.unsqueeze(0).to(device=device)

    model = torch.load(path_manager.get_checkpoint_path(project_name, train_result, checkpoint) / MODEL)

    model.to(device)

    model.eval()
    predicted = model(image)

    top_values, top_indices = predicted.topk(1, dim=1)
    top_values = top_values[0].cpu().detach().numpy()
    top_indices = top_indices[0].cpu().detach().numpy()

    predicted_label = metadata.classes[top_indices[0]]
    max_value = top_values[0]

    return ok(
        data=InferenceResponse(
            label = predicted_label,
            probability = max_value
        )
    )
    """