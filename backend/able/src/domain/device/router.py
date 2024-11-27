from fastapi import APIRouter, Response

from src.domain.device.service import get_device_list
from src.common.utils.response.utils import ok

device_router = APIRouter()

@device_router.get("")
async def get_devices() -> Response:
    return ok(
        data=get_device_list()
    )