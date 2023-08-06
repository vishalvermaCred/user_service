import re
import psycopg2
from uuid import uuid4
from http import HTTPStatus
from fastapi import UploadFile
from fastapi.logger import logger

from app.constants import phone_regex, Tables
from app.database import (
    execute_select_query,
    execute_insert_query,
    execute_user_insertion,
    execute_mongo_select_operation,
)
from app.response_formatter import send_api_response

LOGGER_KEY = "app.service"


async def process_user_details(
    fullname: str,
    username: str,
    email: str,
    phone: str,
    profile_picture: UploadFile,
):
    logger.info(f"{LOGGER_KEY}.process_user_details")
    if phone and not is_phone_valid(phone):
        return await send_api_response("phone number is not valid", False, status_code=HTTPStatus.BAD_REQUEST.value)

    user_exists = await check_if_user_exists(username, email, phone, Tables.psql_users_table.value)
    if user_exists.get("error"):
        return await send_api_response(user_exists.get("error"), False, status_code=HTTPStatus.BAD_REQUEST.value)

    if user_exists.get("user_exists"):
        return await send_api_response(
            "User with given Username/Email/Phone already exists",
            False,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )

    user_id = uuid4().hex
    user_creation_response = await create_user(user_id, fullname, username, email, phone, profile_picture)
    if user_creation_response.get("error"):
        return await send_api_response(
            user_creation_response.get("error"),
            False,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
        )

    return await send_api_response("User Created Successfully", True, status_code=HTTPStatus.OK.value)


def is_phone_valid(phone):
    logger.info(f"{LOGGER_KEY}.is_phone_valid")

    # Check if the phone number matches the regex pattern
    if re.match(phone_regex, phone):
        return True
    else:
        return False


async def check_if_user_exists(username, email, phone, table):
    logger.info(f"{LOGGER_KEY}.check_if_user_exists")
    select_query = f"SELECT user_id FROM {table} WHERE username='{username}' OR email = '{email}' OR phone = '{phone}';"
    user_data = await execute_select_query(select_query)
    logger.debug("data:", user_data)
    if user_data.get("error"):
        return user_data
    user_details = user_data.get("data")
    if user_details:
        return {"user_exists": True}
    return {"user_exists": False}


async def create_user(user_id, fullname, username, email, phone, profile_picture):
    logger.info(f"{LOGGER_KEY}.create_user")
    profile_picture_insert_query = None
    user_data_insert_query = f"INSERT INTO {Tables.psql_users_table.value} (user_id, fullname, username, email, phone) VALUES ('{user_id}', '{fullname}', '{username}', '{email}', '{phone}') RETURNING id;"
    if profile_picture:
        profile_picture_data = await profile_picture.read()
        profile_picture_insert_query = f"INSERT INTO profile (user_id, profile_picture) VALUES ('{user_id}', {psycopg2.Binary(profile_picture_data)}) RETURNING 1;"
    insert_query_response = await execute_insert_query(user_data_insert_query, profile_picture_insert_query)
    logger.debug(f"insert_query_response: {insert_query_response}")
    return insert_query_response


async def get_user_details(user_id, username, email, phone):
    logger.info(f"{LOGGER_KEY}.get_user_details")
    if user_id:
        select_query = f"SELECT users.user_id, users.username, users.fullname, users.email, users.phone, encode(profile.profile_picture, 'base64') as profile_picture FROM users LEFT JOIN profile ON users.user_id = profile.user_id WHERE users.user_id = '{user_id}';"
    else:
        select_query = f"SELECT users.user_id, users.username, users.fullname, users.email, users.phone, encode(profile.profile_picture, 'base64') as profile_picture FROM users LEFT JOIN profile ON users.user_id = profile.user_id WHERE users.email = '{email}' OR users.username = '{username}' OR users.phone = '{phone}';"
    user_data = await execute_select_query(select_query)
    logger.debug("data:", user_data)
    if user_data.get("error"):
        return user_data
    user_details = user_data.get("data")
    if not user_details:
        return await send_api_response(
            "user not found with provided details",
            False,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )
    if len(user_details) > 1:
        return await send_api_response(
            "provided details exists for more than one user",
            False,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )
    user_details = user_details[0]
    response = {
        "user_id": user_details[0],
        "username": user_details[1],
        "fullname": user_details[2],
        "email": user_details[3],
        "phone": user_details[4],
        "profile_picture": user_details[5],
    }
    return await send_api_response(
        "user details fetched successfully",
        True,
        data=response,
        status_code=HTTPStatus.OK.value,
    )


async def process_user_details_using_mongo(
    fullname: str,
    username: str,
    email: str,
    phone: str,
    profile_picture: UploadFile,
):
    logger.info(f"{LOGGER_KEY}.process_user_details_using_mongo")
    if phone and not is_phone_valid(phone):
        return await send_api_response("phone number is not valid", False, status_code=HTTPStatus.BAD_REQUEST.value)

    user_exists = await check_if_user_exists(username, email, phone, Tables.mongo_users_table.value)
    if user_exists.get("error"):
        return await send_api_response(user_exists.get("error"), False, status_code=HTTPStatus.BAD_REQUEST.value)

    if user_exists.get("user_exists"):
        return await send_api_response(
            "User with given Username/Email/Phone already exists",
            False,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )

    user_id = uuid4().hex
    user_creation_response = await create_user_mongo_managed(user_id, fullname, username, email, phone, profile_picture)
    if user_creation_response.get("error"):
        return await send_api_response(
            user_creation_response.get("error"),
            False,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
        )
    return await send_api_response("User Created Successfully", True, status_code=HTTPStatus.OK.value)


async def create_user_mongo_managed(user_id, fullname, username, email, phone, profile_picture):
    logger.info(f"{LOGGER_KEY}.create_user_mongo_managed")
    user_data_insert_query = f"INSERT INTO {Tables.mongo_users_table.value} (user_id, fullname, username, email, phone) VALUES ('{user_id}', '{fullname}', '{username}', '{email}', '{phone}') RETURNING id;"
    insertion_response = await execute_user_insertion(user_id, user_data_insert_query, profile_picture)
    return insertion_response


async def get_user_details_v2(user_id, username, email, phone):
    logger.info(f"{LOGGER_KEY}.get_user_details_v2")
    if user_id:
        user_Data_psql_select_query = f"SELECT user_id, username, fullname, email, phone FROM {Tables.mongo_users_table.value} WHERE user_id='{user_id}';"
    else:
        user_Data_psql_select_query = f"SELECT user_id, username, fullname, email, phone FROM {Tables.mongo_users_table.value} WHERE email = '{email}' OR username = '{username}' OR phone = '{phone}';"
    user_data_from_psql = await execute_select_query(user_Data_psql_select_query)
    logger.debug("data:", user_data_from_psql)
    if user_data_from_psql.get("error"):
        return user_data_from_psql
    user_details = user_data_from_psql.get("data")
    if not user_details:
        return await send_api_response(
            "user not found with provided details",
            False,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )
    if len(user_details) > 1:
        return await send_api_response(
            "provided details exists for more than one user",
            False,
            status_code=HTTPStatus.BAD_REQUEST.value,
        )
    user_details = user_details[0]
    response = {
        "user_id": user_details[0],
        "username": user_details[1],
        "fullname": user_details[2],
        "email": user_details[3],
        "phone": user_details[4],
    }

    mongo_query = {"user_id": response.get("user_id")}
    profile_picture_data = await execute_mongo_select_operation(mongo_query)
    response["profile_picture"] = profile_picture_data
    return await send_api_response(
        "user details fetched successfully",
        True,
        data=response,
        status_code=HTTPStatus.OK.value,
    )
