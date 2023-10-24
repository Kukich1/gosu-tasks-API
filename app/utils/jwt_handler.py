from datetime import datetime, timedelta

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from app.utils.database import get_db, compare
from app.utils.config import SECRET_KEY, ALGORITHM

http_bearer = HTTPBearer()

def create_jwt_token(data: dict, expires_delta: timedelta): 
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(username: str, role: str, expires_delta: timedelta):
    to_encode = {"sub": username, "role": role}
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(http_bearer)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        name: str = payload.get("sub")
        if name is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        db = get_db()
        user = await db['users'].find_one({"name": name, "role": 0})
        if user is None:
            user = await db['users'].find_one({"name": name, "role": 1})
        username = user.get("username")
        print(username)
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

async def get_refresh_token(token: str = Depends(http_bearer)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")