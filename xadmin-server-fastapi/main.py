"""
FastAPI主应用文件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, user, common, settings, message, dept, menu
from app.core.config import settings as app_settings

app = FastAPI(
    title=app_settings.PROJECT_NAME,
    openapi_url=f"{app_settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

# 添加路由
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/system", tags=["user"])
app.include_router(dept.router, prefix="/api/system/dept", tags=["dept"])
app.include_router(menu.router, prefix="/api/system/menu", tags=["menu"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(message.router, prefix="/api/message", tags=["message"])
app.include_router(common.router, prefix="/api/common", tags=["common"])



@app.get("/")
def read_root():
    return {"Hello": "XAdmin FastAPI"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=app_settings.DEBUG,
        log_level=app_settings.LOG_LEVEL.lower()
    )
