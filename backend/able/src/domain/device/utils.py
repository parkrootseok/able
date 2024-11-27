from src.domain.device.schema import DeviceStatus
from src.common.utils.file.path_manager import PathManager
from src.common.utils.file.utils import create_file, get_file
from src.common.utils import json_to_str, str_to_json

path_manager = PathManager()

def get_device_status(name: str) -> DeviceStatus:
    device_file_path = path_manager.get_device_path(name)

    if not device_file_path.exists():
        device_dict = {"status": DeviceStatus.NOT_IN_USE}
        create_file(device_file_path, json_to_str({"status": DeviceStatus.NOT_IN_USE}))
    else:
        device_dict = str_to_json(get_file(device_file_path))

    return device_dict.get("status")

def update_device_status(name: str, status: DeviceStatus):
    device_file_path = path_manager.get_device_path(name)

    create_file(device_file_path, json_to_str({"status": status}))