from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models import SensorData, NonWorkingSensor
from sqlalchemy import text
from datetime import datetime


async def get_sensordata(db: AsyncSession, offset: int = 0, limit: int = 10):
    result = await db.execute(select(SensorData).offset(offset).limit(limit))
    return result.scalars().all()


async def get_sensordata_by_date(
    db: AsyncSession, start_date: datetime, end_date: datetime
):
    result = await db.execute(
        select(SensorData).where(SensorData.received_at.between(start_date, end_date))
    )
    return result.scalars().all()


async def get_last_sensordata(db: AsyncSession):
    result = await db.execute(
        select(SensorData).order_by(SensorData.id.desc()).limit(1)
    )
    return result.scalars().first()


async def get_sensordata_by_id(db: AsyncSession, id: int):
    result = await db.execute(select(SensorData).where(SensorData.id == id))
    return result.scalars().first()


async def purge_sensordata(db: AsyncSession):
    await db.execute(text("TRUNCATE TABLE sensordata CASCADE"))
    await db.commit()
    return {"message": "Sensor data purged successfully"}


async def get_non_working_sensors(db: AsyncSession):
    result = await db.execute(select(NonWorkingSensor))
    return result.scalars().all()


async def purge_sensordata_by_date(
    db: AsyncSession, start_date: datetime, end_date: datetime
):
    await db.execute(
        text(
            "DELETE FROM sensordata WHERE received_at BETWEEN :start_date AND :end_date"
        ),
        {"start_date": start_date, "end_date": end_date},
    )
    await db.commit()
    return {"message": "Sensor data purged successfully"}


async def create_sensordata(db: AsyncSession, sensor_data: SensorData):
    db.add(sensor_data)
    await db.commit()
    await db.refresh(sensor_data)
    return sensor_data
