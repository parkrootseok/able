from src.common.exceptions import BaseCustomException
from starlette import status

class FileNotFoundException(BaseCustomException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class FileUnreadableException(BaseCustomException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class ImageSaveFailException(BaseCustomException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
class DirectoryCreationException(BaseCustomException):
    def __init__(self, detail: str = "디렉터리 생성에 실패했습니다."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class DirectoryUpdateException(BaseCustomException):
    def __init__(self, detail: str = "디렉터리 수정에 실패했습니다."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )