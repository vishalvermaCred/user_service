from logging import getLogger

import psycopg2

from app.settings import USER_DB

logger = getLogger(__name__)

psg_db_instance = None


async def init_database(db_name):
    global psg_db_instance
    if not psg_db_instance:
        logger.info(f"Initializing {db_name} database connection..")
        psg_db_instance = psycopg2.connect(
            host=USER_DB.get("HOST"),
            port=USER_DB.get("PORT"),
            user=USER_DB.get("USER"),
            database=USER_DB.get("NAME"),
            password=USER_DB.get("PASSWORD"),
        )
        logger.info("Database connection established.")


async def disconnect_db():
    if psg_db_instance:
        await psg_db_instance.close()
