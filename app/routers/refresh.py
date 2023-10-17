from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException

from app.utils.jwt_handler import get_refresh_token, create_jwt_token, JWTError
from app.utils.database import get_db

router = APIRouter(
    prefix="/token",
    tags=["Refresh Token"]
)

@router.post("/refresh/")
async def refresh_access_token(name: str = Depends(get_refresh_token)):
    try:
        db = get_db()
        user_collection = db['users']
        user = await user_collection.find_one({"name": name}, {'_id': 0})
        role_for_token = user['role']
        if name is None or role_for_token is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        access_token_expires = timedelta(minutes=240)
        access_token = create_jwt_token(
            data={"sub": name},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "username": name, "role": role_for_token}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")