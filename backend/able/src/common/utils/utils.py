import base64
import json

from typing import Any, Dict, List
from pydantic import BaseModel
from src.common.utils.logger.utils import get_logger

logger = get_logger(__name__)

def str_to_json(data: str) -> Dict[str, Any]:

    if not isinstance(data, str):
        logger.error(f"Invalid data type: Expected a JSON string, but got {type(data)}")
        raise TypeError("Invalid data type: Expected a JSON string.")

    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        logger.error(f"JSON 디코딩 실패: {e}. 데이터: {data[:50]}...", exc_info=True)
        raise

def json_to_str(obj: Any) -> str:
    if isinstance(obj, BaseModel):
        data_dict = obj.model_dump()
    elif isinstance(obj, dict):
        data_dict = obj
    else:
        raise TypeError("지원되지 않는 데이터 타입입니다. Pydantic 모델 또는 딕셔너리가 필요합니다.")

    try:
        return json.dumps(data_dict, ensure_ascii=False, indent=4)
    except (TypeError, json.JSONDecodeError, UnicodeEncodeError) as e:
        logger.error(f"JSON 직렬화 실패: {e}", exc_info=True)
        raise

def encode_image_to_base64(image_data: bytes) -> str:
    base64_str = base64.b64encode(image_data).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_str}"
    
def handle_pagination(items: List[Any], page: int, page_size: int) -> List[Any]:
    items_length = len(items)
    if items_length == 0:
        logger.info("빈 페이지 조회")
        return []

    if(page * page_size) >= items_length:
        logger.error("범위를 넘어간 페이지 조회")
        return None
    
    if (page * page_size + page_size) > items_length:
        logger.info(f"마지막 페이지 조회 성공")
        return items[page * page_size:]
    
    logger.info(f"{page + 1}페이지 조회 성공")
    return items[page * page_size:page * page_size + page_size]

def has_next_page(items_length: int, index: int, size: int) -> bool:
    if(index * size + size < items_length):
        return True
    return False