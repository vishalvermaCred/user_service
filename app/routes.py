from fastapi import APIRouter, Form
from fastapi.logger import logger
from pydantic import EmailStr

router = APIRouter()

LOGGER_KEY = "app.router"


@router.get("/public/healthz", tags=["Root"])
async def health_check():
    return {"message": "OK"}


@router.post("/signup")
async def _user_signup(
    full_name: str = Form(..., description="email of the user"),
    email: EmailStr = Form(None, description="email of the user"),
    username: str = Form(..., description="unique username of the user"),
    phone: str = Form(None, description="phone number of the user"),
    profile_picture=Form(None, description="profile picture of user"),
):
    logger.info(f"{LOGGER_KEY}._user_signup")
    return {"success": True}
