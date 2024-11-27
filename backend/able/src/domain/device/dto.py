from src.domain.device.schema import Device
from src.common.utils.response.schemas import ImmutableBaseModel

class DeviceListResponse(ImmutableBaseModel):
    devices: list[Device]