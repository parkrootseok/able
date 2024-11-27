from starlette import status
from src.common.exceptions import BaseCustomException

class BlockNotFoundException(BaseCustomException):
    def __init__(self, keyword: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block with keyword '{keyword}' not found."
        )