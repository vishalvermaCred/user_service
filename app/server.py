import logging

from fastapi import FastAPI
from fastapi.logger import logger

from app.constants import USER_DB
from app.database import disconnect_db, init_database
from app.redis_connection import init_redis
from app.routes import router
from app.settings import BASE_ROUTE, LOG_LEVEL, SERVICE_NAME

extra = {"app_name": SERVICE_NAME}
logging.basicConfig(level=LOG_LEVEL, format=f"%(asctime)s {SERVICE_NAME} %(levelname)s : %(message)s")
logger = logging.getLogger(__name__)
logger = logging.LoggerAdapter(logger, extra)

app = FastAPI(
    docs_url=f"{BASE_ROUTE}/docs",
    redoc_url=f"{BASE_ROUTE}/redocs",
    openapi_url=f"{BASE_ROUTE}/openapi.json",
)
app.include_router(router, tags=["User Management"], prefix=BASE_ROUTE)


@app.on_event("startup")
async def startup_event():
    logger.info("SERVER STARTING...")
    await init_database(USER_DB)
    logger.info("User Database initialization completed.")
    await init_redis()
    logger.info("Redis Connected")


@app.on_event("shutdown")
async def shutdown_event():
    await disconnect_db()
    logger.info("App Shutdown Completed.")
