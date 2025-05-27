from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Float,
    func,
    Boolean,
)
from src.database import Base
from sqlalchemy.orm import relationship


class SensorData(Base):
    Air_humidity_ = Column(Float)
    Air_temperature_C = Column(Float)
    Pressure_KPa = Column(Float)
    Soil_Humidity = Column(Float)
    Soil_Moisture = Column(Float)
    Temperature = Column(Float)
    Time = Column(Float)
    Wind_speed_Kmh = Column(Float)
    number_of_working_sensors = Column(Float)
    prediction = Column(Integer)
    rainfall = Column(Float)

    received_at = Column(DateTime(timezone=True), default=func.now())
    timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    non_working_sensors = relationship(
        "NonWorkingSensor", backref="sensordata", cascade="all, delete-orphan"
    )


class NonWorkingSensor(Base):
    sensor_name = Column(String, nullable=False)
    sensor_data_id = Column(Integer, ForeignKey("sensordata.id"))


class User(Base):
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
