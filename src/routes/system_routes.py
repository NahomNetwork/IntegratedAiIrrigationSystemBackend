from datetime import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from src.routes.socketio.route import sio
from src.models import SensorData, NonWorkingSensor
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schema import SensorDataRequest
from sqlalchemy.future import select
from src.schema import FeatureData
from sqlalchemy import text
import numpy as np


system_router = APIRouter(prefix="/system")


@system_router.post("/sensor_data")
async def receive_sensordata(
    req: SensorDataRequest, request: Request, db: AsyncSession = Depends(get_db)
):
    try:
        sensor_data_dict = req.model_dump()

        features_raw = FeatureData(**sensor_data_dict)

        model = request.app.state.model
        if not model:
            raise HTTPException(status_code=503, detail="Model not initialized")

        features = np.array([list(features_raw.model_dump().values())])
        prediction = model.predict(features)[0]

        non_working_sensors_data = sensor_data_dict.pop("Non_working_sensors", [])
        db_item = SensorData(
            **sensor_data_dict,
            prediction=prediction,
            non_working_sensors=[
                NonWorkingSensor(sensor_name=item) for item in non_working_sensors_data
            ],
        )

        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)

        await sio.emit("sensor_data", db_item)

        return {"results": db_item}
    except Exception as e:
        raise HTTPException(500, detail=e)


@system_router.get("/get_sensordata")
async def get_sensordata(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SensorData).offset(0).limit(10))
    data = result.scalars().all()

    return {"results": data}


@system_router.get("/get_sensordata/last")
async def get_last_sensordata(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SensorData).order_by(SensorData.id.desc()).limit(1)
    )
    data = result.scalars().first()

    if not data:
        raise HTTPException(status_code=404, detail="Sensor data not found")

    return {"results": data}


@system_router.get("/get_sensordata/{id}")
async def get_sensordata_by_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SensorData).where(SensorData.id == id))
    data = result.scalars().first()

    if not data:
        raise HTTPException(status_code=404, detail="Sensor data not found")

    return {"results": data}


@system_router.delete("/sensordata/purge")
async def purge_sensordata(db: AsyncSession = Depends(get_db)):
    await db.execute(text("TRUNCATE TABLE sensordata CASCADE"))
    await db.commit()
    return {"message": "Sensor data purged successfully"}


@system_router.get("/non_working_sensors")
async def get_non_working_sensors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NonWorkingSensor))
    data = result.scalars().all()

    return {"results": data}


# @system_router.get("/sensordata/purge-by-date")
# async def purge_sensordata_by_date(
#     start_date: str, end_date: str, db: AsyncSession = Depends(get_db)
# ):
#     await db.execute(
#         text(
#             "DELETE FROM sensordata WHERE received_at BETWEEN :start_date AND :end_date"
#         ),
#         {"start_date": start_date, "end_date": end_date},
#     )
#     await db.commit()
#     return {"message": "Sensor data purged successfully"}


@system_router.get("/sensordata/purge-by-date")
async def purge_sensordata_by_date(
    start_date: str, end_date: str, db: AsyncSession = Depends(get_db)
):
    """
    Purge sensor data between start_date and end_date (inclusive).
    Dates must be in ISO 8601 format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.
    """
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO 8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS).")

    try:
        await db.execute(
            text(
                "DELETE FROM sensordata WHERE received_at BETWEEN :start_date AND :end_date"
            ),
            {"start_date": start_dt, "end_date": end_dt},
        )
        await db.commit()
        return {"message": "Sensor data purged successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error purging sensor data: {str(e)}")

