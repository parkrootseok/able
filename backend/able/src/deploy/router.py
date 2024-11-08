import src.deploy.service as service
from fastapi import APIRouter
from starlette.responses import Response
from src.response.utils import accepted
from .schemas import RegisterApiRequest

deploy_router = router = APIRouter()

@router.get("/run")
def run() -> Response:
    service.run()
    return accepted()

@router.get("/stop")
def stop() -> Response:
    service.stop()
    return accepted()

@router.post("/routers")
def register_router(request: RegisterApiRequest) -> Response:
    service.register_router(request)
    return accepted()

@router.delete("/routers")
def remove_router(uri: str) -> Response:
    service.remove_router(uri)
    return accepted()

@router.post("/restart")
def restart() -> Response:
    service.stop()
    service.run()
    return accepted()