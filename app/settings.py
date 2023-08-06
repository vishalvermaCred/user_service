from os import getenv

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

ENV = getenv("ENV", "")
SERVICE_NAME = getenv("SERVICE_NAME", "")
APP_NAME = getenv("APP_NAME", "User Service")

BASE_ROUTE = getenv("BASE_ROUTE")
LOG_LEVEL = getenv("LOG_LEVEL", "INFO")

USER_DB = {
    "HOST": getenv("DB_HOST"),
    "PORT": getenv("DB_PORT"),
    "NAME": getenv(f"USER_DB_NAME"),
    "PASSWORD": getenv("USER_DB_PASSWORD"),
    "USER": getenv("USER_DB_USER"),
}

REDIS_CONFIG = {
    "HOST": getenv("REDIS_HOST", "localhost"),
    "PORT": getenv("REDIS_PORT", "6379"),
}
