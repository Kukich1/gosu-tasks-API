from datetime import timedelta
from werkzeug.security import generate_password_hash
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.models.models import User
from app.models.models import UserLogin
from app.utils.database import register_new_user, authenticate_user
from app.utils.jwt_handler import create_jwt_token, create_refresh_token

router = APIRouter(
    prefix="/auth",
    tags=["Авторизация"]
)

#Занести нового пользователя в бд
@router.post("/register/")
async def register(user: User):
    try:
        password_hash = generate_password_hash(user.password)
        user_data = user.dict()
        user_data["password"] = password_hash
        user_data["id"] = str(uuid4())
        await register_new_user(user_data)
        return {"message": "User registered successfully"}
    except Exception as error:
        return "Nope("
    
#Аутентификация и получение токена    
@router.post("/login/")
async def login_for_access_token(user_data: UserLogin):
    user = await authenticate_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=120)                                                                                                                                                                                         
    access_token = create_jwt_token(
        data={"sub": user["name"]},
        expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_refresh_token(user['name'],user['role'], expires_delta = refresh_token_expires)
    return {"access_token": access_token, "refresh_token": refresh_token, "role": user['role'], "name": user['name'], "username": user['username']}
