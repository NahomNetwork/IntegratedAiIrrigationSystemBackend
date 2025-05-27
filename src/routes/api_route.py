from fastapi import APIRouter
from src.routes.system_routes import system_router
from src.routes.auth import auth_router

api_route = APIRouter(prefix="/api")

api_route.include_router(system_router)
api_route.include_router(auth_router, prefix="/auth", tags=["Authentication"])
