from http import HTTPStatus
from fastapi import APIRouter, Form
from fastapi.logger import logger
from pydantic import EmailStr

from app.response_formatter import send_api_response
from app.service import get_user_details, process_user_details, get_user_details_v2, process_user_details_using_mongo

router = APIRouter()

LOGGER_KEY = "app.router"


@router.get("/public/healthz", tags=["Root"])
async def health_check():
    return {"message": "OK"}


@router.post("/signup")
async def _user_signup(
    fullname: str = Form(..., description="email of the user"),
    username: str = Form(..., description="unique username of the user"),
    email: EmailStr = Form(None, description="email of the user"),
    phone: str = Form(None, description="phone number of the user"),
    profile_picture=Form(None, description="profile picture of user"),
):
    """
    this api stores user details in postgres
    it stores profile picture in profile table in postgres and rest details in users table in postgres
    """
    logger.info(f"{LOGGER_KEY}._user_signup")
    kwargs = {
        "fullname": fullname,
        "username": username,
        "email": email,
        "phone": phone,
        "profile_picture": profile_picture,
    }
    response = await process_user_details(**kwargs)
    return response


@router.get("/user_details")
async def _fetch_user_details(user_id: str = None, username: str = None, email: EmailStr = None, phone: str = None):
    """
    this api fetches user details in postgres
    it fetches profile picture from profile table in postgres and rest details from users table in postgres with join
    """
    logger.info(f"{LOGGER_KEY}._fetch_user_details")
    if not (user_id or username or email or phone):
        return await send_api_response(
            "please provide UserId/Username/Email/Phone", False, HTTPStatus.BAD_REQUEST.value
        )

    response = await get_user_details(user_id, username, email, phone)
    return response


@router.post("/signup/v2")
async def _user_signup_v2(
    fullname: str = Form(..., description="email of the user"),
    username: str = Form(..., description="unique username of the user"),
    email: EmailStr = Form(None, description="email of the user"),
    phone: str = Form(None, description="phone number of the user"),
    profile_picture=Form(None, description="profile picture of user"),
):
    """
    this api stores user details in postgres and mongoDB
    it profile picture in profile_mongo table in mongoDB and rest details in users_mongo table in postgres
    """
    logger.info(f"{LOGGER_KEY}._user_signup_v2")
    kwargs = {
        "fullname": fullname,
        "username": username,
        "email": email,
        "phone": phone,
        "profile_picture": profile_picture,
    }
    response = await process_user_details_using_mongo(**kwargs)
    return response


@router.get("/user_details/v2")
async def _fetch_user_details_v2(user_id: str = None, username: str = None, email: EmailStr = None, phone: str = None):
    """
    this api fetches user details in postgres
    it fetches profile picture from profile_mongo table in mongoDB and rest details from users_mongo table in postgres
    """
    logger.info(f"{LOGGER_KEY}._fetch_user_details_v2")
    if not (user_id or username or email or phone):
        return await send_api_response(
            "please provide UserId/Username/Email/Phone", False, HTTPStatus.BAD_REQUEST.value
        )

    response = await get_user_details_v2(user_id, username, email, phone)
    return response
