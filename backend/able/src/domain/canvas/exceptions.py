from starlette import status
from src.common.exceptions import BaseCustomException


class CanvasNotFoundException(BaseCustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canvas not found or unreadable"
        )
class CanvasSaveException(BaseCustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while saving the canvas data."
        )