from sqlalchemy.ext.asyncio import AsyncSession
from src.models import User
from src.schema import UserCreate
from src.services.auth import hash_password
from sqlalchemy.future import select
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from src.database import get_db
from fastapi import HTTPException, status
from src import config
from jose import jwt, JWTError

oauth2_scheme = HTTPBearer()


async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def check_user_exists(db: AsyncSession, username: str, email: str):
    user = await db.execute(
        select(User).filter((User.username == username) | (User.email == email))
    )
    user = user.scalars().first()
    if user:
        return True
    return False


async def create_user(db: AsyncSession, user_in: UserCreate):
    hashed_pw = hash_password(user_in.password)

    user = User(**user_in.model_dump(exclude={"password"}), hashed_password=hashed_pw)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    jwt_token = token.credentials

    try:
        payload = jwt.decode(
            jwt_token, config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user


async def get_admin_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    user = await get_current_user(token, db)
    if not bool(user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    return user
