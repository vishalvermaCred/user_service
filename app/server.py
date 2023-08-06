import logging

from fastapi import FastAPI
from fastapi.logger import logger

from app.constants import PSQL_USER_DB, MONGO_USER_DB
from app.database import disconnect_db, init_psql_database, init_mongo_database
from app.redis_connection import init_redis
from app.routes import router
from app.settings import BASE_ROUTE, LOG_LEVEL, SERVICE_NAME

extra = {"app_name": SERVICE_NAME}
logging.basicConfig(level=LOG_LEVEL, format=f"%(asctime)s {SERVICE_NAME} %(levelname)s : %(message)s")
logger = logging.getLogger(__name__)
logger = logging.LoggerAdapter(logger, extra)

# Intializing app
app = FastAPI(
    docs_url=f"{BASE_ROUTE}/docs",
    redoc_url=f"{BASE_ROUTE}/redocs",
    openapi_url=f"{BASE_ROUTE}/openapi.json",
)
app.include_router(router, tags=["User Management"], prefix=BASE_ROUTE)


@app.on_event("startup")
async def startup_event():
    logger.info("SERVER STARTING...")
    await init_psql_database(PSQL_USER_DB)
    logger.info("User PSQL Database initialization completed.")
    await init_mongo_database(MONGO_USER_DB)
    logger.info("User MONGO Database initialization completed.")
    await init_redis()
    logger.info("Redis Connected")


@app.on_event("shutdown")
async def shutdown_event():
    await disconnect_db()
    logger.info("App Shutdown Completed.")
