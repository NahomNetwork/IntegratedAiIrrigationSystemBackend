from pydantic import BaseModel
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
