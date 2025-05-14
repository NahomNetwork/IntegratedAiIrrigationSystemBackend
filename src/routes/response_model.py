from pydantic import BaseModel
from typing import List, Optional


class SensorDataRequest(BaseModel):
    Air_humidity_: float
    Air_temperature_C: float
    Soil_Humidity: float
    Soil_Moisture: float
    working_sensors: int
    Temperature: float
    Non_working_sensors: List[str]
