import psycopg2
from logging import getLogger


from app.constants import USER_DB
from app.settings import USER_DB

logger = getLogger(__name__)
LOGGER_KEY = "app.database"

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


async def get_db(db_name):
    logger.info(f"{LOGGER_KEY}.get_db")
    global psg_db_instance
    if not psg_db_instance:
        psg_db_instance = await init_database(db_name)
    return psg_db_instance


async def execute_select_query(query):
    logger.info(f"{LOGGER_KEY}.execute_select_query")
    db_instance = await get_db(USER_DB)
    response = {"error": None}
    try:
        db_cursor = db_instance.cursor()
        logger.info(f"query - {query}")
        db_cursor.execute(query)
        user_details = db_cursor.fetchall()
        response = {"data": user_details}
    except Exception as e:
        logger.error(f"{LOGGER_KEY}.execute_select_query.exception: {str(e)}")
        response = {"error": str(e)}
    return response


async def execute_insert_query(user_data_insert_query, profile_picture_insert_query=None):
    logger.info(f"{LOGGER_KEY}.execute_insert_query")
    db_instance = await get_db(USER_DB)
    response = {"error": None}
    try:
        db_cursor = db_instance.cursor()
        logger.info(f"user_data_insert_query - {user_data_insert_query}")
        logger.info(f"profile_picture_insert_query - {profile_picture_insert_query}")
        db_cursor.execute(user_data_insert_query)
        if profile_picture_insert_query:
            db_cursor.execute(profile_picture_insert_query)
        db_instance.commit()
        user_details = db_cursor.fetchall()
        response = {"data": user_details}
    except Exception as e:
        logger.error(f"{LOGGER_KEY}.execute_insert_query.exception: {str(e)}")
        response = {"error": str(e)}
    return response


async def disconnect_db():
    if psg_db_instance:
        await psg_db_instance.close()
