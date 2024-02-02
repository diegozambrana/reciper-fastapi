from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import jwt, JWTError

from models import User
from database import get_db


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

SECRET_KEY = 'cb4bea6692b8978c58124c0d91f4706fc8fa238dce00f92b34c1a526f4235f61'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
db_dependency = Annotated[Session, Depends(get_db)]
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

class CreateUser(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str


class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expire = datetime.utcnow() + expires_delta
    encode.update({"exp": expire})
    encoded_jwt = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



@router.post("/register")
async def register_user(
    db: db_dependency,
    user: CreateUser,
):
    print('register_user')
    created_user = User(
        username=user.username,
        email=user.email,
        hashed_password=bcrypt_context.hash(user.password),
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=True
    )

    db.add(created_user)
    db.commit()
    db.refresh(created_user)
    return created_user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    db: db_dependency,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if user is None or not bcrypt_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    token = create_access_token(user.username, user.id, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}