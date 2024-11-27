from fastapi import status
from src.common.exceptions import BaseCustomException

class ProjectNameAlreadyExistsException(BaseCustomException):
    def __init__(self, detail):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )