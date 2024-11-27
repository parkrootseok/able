from starlette import status
from src.common.exceptions import BaseCustomException

# 메타데이터 파일 생성 실패 시 예외 (500 Internal Server Error)
class MetadataCreationException(BaseCustomException):
    def __init__(self, path_name: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"'{path_name}'에 대한 메타데이터 파일 생성에 실패했습니다."
        )

# 라우터 파일 생성 실패 시 예외 (500 Internal Server Error)
class RouterCreationException(BaseCustomException):
    def __init__(self, path_name: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"'{path_name}'에 대한 라우터 파일 생성에 실패했습니다."
        )

# main.py 파일 업데이트 실패 시 예외 (500 Internal Server Error)
class MainFileUpdateException(BaseCustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"main.py 파일 수정에 실패했습니다."
        )

# 서버 중지 실패 시 예외 (500 Internal Server Error)
class ServerStopException(BaseCustomException):
    def __init__(self, message: str = "서버 중지에 실패했습니다."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )

# 서버 프로세스 트리 종료 실패 시 예외 (500 Internal Server Error)
class ProcessTerminationException(BaseCustomException):
    def __init__(self, pid: int):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PID {pid}에 대한 프로세스 트리 종료에 실패했습니다."
        )

# 파일을 찾을 수 없을 때 예외 (404 Not Found)
class FileNotFoundException(BaseCustomException):
    def __init__(self, path: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"파일을 찾을 수 없습니다: {path}"
        )

# 파일 읽기 실패 시 예외 (500 Internal Server Error)
class FileReadException(BaseCustomException):
    def __init__(self, path: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일을 읽는 데 실패했습니다: {path}"
        )

# 파일 제거 실패 시 예외 (500 Internal Server Error)
class FileDeletionException(BaseCustomException):
    def __init__(self, path: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 삭제에 실패했습니다: {path}"
        )

# 라우터 중복 생성 시 예외 (400 Bad Request)
class AlreadyExistsApiException(BaseCustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 API입니다."
        )

# 요청된 API가 존재하지 않을 때 예외 (404 Not Found)
class ApiNotFoundException(BaseCustomException):
    def __init__(self, uri: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"해당 URI에 대한 API를 찾을 수 없습니다: {uri}"
        )

# 이미 실행 중인 서버 시작 시도 시 예외 (400 Bad Request)
class AlreadyRunException(BaseCustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="서버가 이미 실행 중입니다."
        )

# 실행 중이지 않은 서버 중지 시도 시 예외 (400 Bad Request)
class AlreadyStopException(BaseCustomException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="서버가 실행 중이 아닙니다."
        )