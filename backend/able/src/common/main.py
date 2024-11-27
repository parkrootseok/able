import uvicorn

from pathlib import Path
from fastapi import FastAPI, HTTPException,Request
from starlette.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from src.domain.block.router import block_router
from src.domain.checkpoints.router import checkpoint_router
from src.domain.device.router import device_router
from src.domain.deploy.router import deploy_router
from src.domain.train.router import train_router
from src.domain.canvas.router import canvas_router
from src.domain.project.router import project_router
from src.domain.analysis.router import analysis_router
from src.common.exceptions import BaseCustomException
from src.domain.train_log.router import train_log_router
from src.domain.validation.router import validation_router

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4173",
    "http://localhost:5173",
    "http://localhost:5000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(train_router, prefix="/trains", tags=["학습"])

app.include_router(train_log_router, prefix="/projects", tags=["학습 결과"])

app.include_router(block_router, prefix="/blocks", tags=["블록"])

app.include_router(project_router, prefix="/projects", tags=["프로젝트"])

app.include_router(canvas_router, prefix="/canvas", tags=["캔버스"])

app.include_router(validation_router, prefix="/validation", tags=["확인"])

app.include_router(analysis_router, prefix="/analyses", tags=["분석"])

app.include_router(checkpoint_router, prefix="/checkpoints", tags=["체크포인트"])

app.include_router(deploy_router, prefix="/deploy", tags=["배포"])

app.include_router(device_router, prefix="/devices", tags=["디바이스"])

base_dir = Path(__file__).parent.parent

# assets 폴더를 정적 파일 경로로 설정
app.mount("/assets", StaticFiles(directory=base_dir / "static/assets"), name="assets")
app.mount("/fonts", StaticFiles(directory=base_dir / "static/fonts"), name="fonts")
app.mount("/favicon.ico", StaticFiles(directory=base_dir / "static"), name="favicon.ico")

# static 폴더를 템플릿 경로로 설정
templates = Jinja2Templates(directory=base_dir / "static")

@app.get("/favicon.ico", response_class=FileResponse)
async def favicon():
    return FileResponse(base_dir / "static" / "favicon.ico")

# React index.html로 라우팅
@app.get("/", response_class=HTMLResponse)
async def serve_react_app(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.exception_handler(HTTPException)
async def base_custom_exception_handler(request: Request, exc: BaseCustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, workers=3)
