import math
from datetime import datetime

def parse_train_result_date(folder_name: str) -> str:
    try:
        # "20241107_110022" -> "2024.11.07 11:00"
        dt = datetime.strptime(folder_name, "%Y%m%d_%H%M%S")
        return dt.strftime("%Y.%m.%d %H:%M")
    except ValueError:
        return ""

def format_float(accuracy_value: float) -> str:
    # accuracy -> percentage
    return f"{math.floor(accuracy_value * 100)}"