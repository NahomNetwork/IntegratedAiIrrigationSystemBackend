from fastapi import APIRouter
from src.routes.system_routes import system_router

api_route = APIRouter(prefix="/api")

api_route.include_router(system_router)
