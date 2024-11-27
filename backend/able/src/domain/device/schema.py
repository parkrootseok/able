from src.common.utils.response.schemas import ImmutableBaseModel
from enum import Enum

class DeviceStatus(str, Enum):
    IN_USE = "in_use"
    NOT_IN_USE = "not_in_use"

class Device(ImmutableBaseModel):
    index: int
    name: str
    status: DeviceStatus