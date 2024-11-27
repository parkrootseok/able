from math import ceil

from src.common.utils.file.path_manager import PathManager
from src.common.utils.file.utils import get_file
from src.domain.train_log.utils import parse_train_result_date, format_float
from src.domain.train_log.schemas import TrainLogResponse, TrainSummary
from src.common.utils import str_to_json, handle_pagination
from src.common.utils.file.constants import *
from src.common.utils.file.exceptions import FileNotFoundException

path_manager = PathManager()

def get_train_logs(title:str, page:int, page_size:int) -> TrainLogResponse :

    train_results_path = path_manager.get_train_results_path(title)

    sorted_train_dirs = sorted(train_results_path.iterdir(), reverse=False)

    train_results = []

    for folder_path in sorted_train_dirs:
        metadata_path = folder_path / METADATA
        performance_metrics_path = folder_path / PERFORMANCE_METRICS

        metadata = str_to_json(get_file(metadata_path))
        formatted_date = parse_train_result_date(folder_path.name)

        if formatted_date == "":
            continue

        index = len(train_results) + 1

        try:
            performance_data = str_to_json(get_file(performance_metrics_path))
            raw_accuracy = performance_data["metrics"].get("accuracy")
            accuracy = format_float(raw_accuracy) if raw_accuracy is not None else "0"
            accuracy = accuracy + "%"
        except FileNotFoundException as e:
            accuracy = "-"

        train_result = TrainSummary(
            index=index,
            origin_dir_name=folder_path.name,
            date=formatted_date,
            accuracy=accuracy,
            status=metadata["status"]
        )

        train_results.append(train_result)

    train_results.reverse()

    paginated_train_results = handle_pagination(train_results, page, page_size)

    if paginated_train_results is None:
        return None

    result = TrainLogResponse(total_pages=ceil(len(train_results)/page_size), train_summaries=paginated_train_results)
    return result