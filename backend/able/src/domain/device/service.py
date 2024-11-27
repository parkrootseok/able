import torch

from src.domain.device.dto import DeviceListResponse
from src.domain.device.schema import Device
from src.domain.device.utils import get_device_status
from src.common.utils.file.path_manager import PathManager

import os

path_manager = PathManager()

def get_device_list() -> DeviceListResponse:


    device_list = [Device(index=-1, name='cpu', status=get_device_status('cpu'))]

    for index in range(torch.cuda.device_count()):
        name = torch.cuda.get_device_name(index)

        device_list.append(Device(index=index, name=name, status=get_device_status(name)))

    return DeviceListResponse(devices=device_list)