from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.schema import UserCreate, Token, UserResponse, UserLogin
from src.database import get_db
from src.services import user as user_service, auth as auth_service
from src.models import User
from src.services.user import get_current_user

auth_router = APIRouter()


@auth_router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await user_service.check_user_exists(
        db, user_in.username, user_in.email
    )
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists",
        )
    return await user_service.create_user(db, user_in)


@auth_router.post("/login", response_model=Token)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user_by_email(db, user_in.email)
    if not user or not auth_service.verify_password(
        user_in.password, str(user.hashed_password)
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth_service.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@auth_router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
