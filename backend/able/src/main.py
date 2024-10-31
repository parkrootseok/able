import uvicorn
from fastapi import FastAPI, HTTPException,Request
from starlette.responses import JSONResponse

from src.block.router import block_router
from src.canvas.router import router as canvas_router
from src.project.router import router as project_router
from src.exceptions import BaseCustomException
from src.train.router import router

app = FastAPI()

app.include_router(block_router, prefix="/blocks", tags=["블록"])

app.include_router(project_router, prefix="/projects", tags=["프로젝트"])

app.include_router(canvas_router, prefix="/projects/canvas", tags=["캔버스"])

app.include_router(router, prefix="/train", tags=["학습"])

@app.exception_handler(HTTPException)
async def base_custom_exception_handler(request: Request, exc: BaseCustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", port=5000, log_level="info")

