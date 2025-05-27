from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class FeatureData(BaseModel):
    Temperature: float
    Soil_Humidity: float
    Time: float
    Soil_Moisture: float
    rainfall: float
    Air_temperature_C: float
    Wind_speed_Kmh: float
    Air_humidity_: float
    Pressure_KPa: float


class InputData(BaseModel):
    features: FeatureData


class PredictionResult(BaseModel):
    prediction: float


class SensorDataRequest(BaseModel):
    Air_humidity_: float
    Air_temperature_C: float
    Soil_Humidity: float
    Soil_Moisture: float
    Temperature: float
    Non_working_sensors: Optional[List[str]]
    Pressure_KPa: float
    Time: float
    Wind_speed_Kmh: float
    rainfall: float
    number_of_working_sensors: Optional[float]
    received_at: Optional[datetime]
    timestamp: Optional[datetime]


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    first_name: str
    last_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    first_name: str
    last_name: Optional[str] = None
    is_active: bool
    is_superuser: bool


class UserLogin(BaseModel):
    email: str
    password: str
