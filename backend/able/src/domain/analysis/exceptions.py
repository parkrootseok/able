from fastapi import status
from src.common.exceptions import BaseCustomException

class ModelLoadException(BaseCustomException):
    def __init__(self, detail):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )