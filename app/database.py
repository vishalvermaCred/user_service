import base64
import psycopg2
import motor.motor_asyncio
from logging import getLogger


from app.constants import PSQL_USER_DB, MONGO_USER_DB, Tables
from app.settings import USER_DB as psql_user_config, MONGO_URI

logger = getLogger(__name__)
LOGGER_KEY = "app.database"

psg_db_instance = None
mongo_db_instance = None


async def init_psql_database(db_name):
    """this function will initialize the postgres database connection

    Args:
        db_name (_type_): to keep it generic, any psql db_name can be provided
    """
    global psg_db_instance
    if not psg_db_instance:
        logger.info(f"Initializing psql {db_name} database connection..")
        psg_db_instance = psycopg2.connect(
            host=psql_user_config.get("HOST"),
            port=psql_user_config.get("PORT"),
            user=psql_user_config.get("USER"),
            database=psql_user_config.get("NAME"),
            password=psql_user_config.get("PASSWORD"),
        )
        logger.info("PSQL Database connection established.")


async def init_mongo_database(db_name):
    """this function will initialize the mongo database connection

    Args:
        db_name (_type_): to keep it generic, any mongo db_name can be provided
    """
    global mongo_db_instance
    if mongo_db_instance == None:
        logger.info(f"Initializing mongo {db_name} database connection..")
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        mongo_db_instance = mongo_client[db_name]
        logger.info("MONGO Database connection established.")


async def get_psql_db(db_name):
    """
    retrieve psql db connection
    """
    logger.info(f"{LOGGER_KEY}.get_psql_db")
    global psg_db_instance
    if not psg_db_instance:
        psg_db_instance = await init_psql_database(db_name)
    return psg_db_instance


async def get_mongo_db(db_name):
    """
    retrieve mongo db connection
    """
    logger.info(f"{LOGGER_KEY}.get_mongo_db")
    global mongo_db_instance
    if mongo_db_instance == None:
        mongo_db_instance = await init_mongo_database(db_name)
    return mongo_db_instance


async def execute_select_query(query):
    logger.info(f"{LOGGER_KEY}.execute_select_query")
    db_instance = await get_psql_db(PSQL_USER_DB)
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
    db_instance = await get_psql_db(PSQL_USER_DB)
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


async def execute_user_insertion(user_id, user_data_insert_query, profile_picture):
    logger.info(f"{LOGGER_KEY}.execute_user_insertion")
    if profile_picture:
        mongo_db = await get_mongo_db(MONGO_USER_DB)
        # gridfs_bucket = AsyncIOMotorGridFSBucket(mongo_db)
        collection = mongo_db[Tables.mongo_profile_table.value]
        profile_picture_data = await profile_picture.read()
        base64_image = base64.b64encode(profile_picture_data)
        document = {"user_id": user_id, "profile_picture": base64_image}
        try:
            collection.insert_one(document)
        except Exception as e:
            logger.error(f"error while inserting profile picture: {str(e)}")
            return {"error": "error"}
    db_instance = await get_psql_db(PSQL_USER_DB)
    response = {"error": None}
    try:
        db_cursor = db_instance.cursor()
        logger.info(f"user_data_insert_query - {user_data_insert_query}")
        db_cursor.execute(user_data_insert_query)
        db_instance.commit()
        user_details = db_cursor.fetchall()
        response = {"data": user_details}
    except Exception as e:
        logger.error(f"{LOGGER_KEY}.execute_insert_query.exception: {str(e)}")
        response = {"error": "error"}
    return response


async def execute_mongo_select_operation(mongo_query):
    logger.info(f"{LOGGER_KEY}.execute_mongo_select_operation")
    mongo_db = await get_mongo_db(MONGO_USER_DB)
    collection = mongo_db[Tables.mongo_profile_table.value]
    document = await collection.find_one(mongo_query)
    base64_image = document.get("profile_picture")
    binary_image = base64.b64decode(base64_image)
    base64_encoded_image = base64.b64encode(binary_image).decode("utf-8")
    return base64_encoded_image


async def disconnect_db():
    if psg_db_instance:
        await psg_db_instance.close()
