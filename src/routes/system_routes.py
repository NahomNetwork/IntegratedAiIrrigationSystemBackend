from datetime import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from src.routes.socketio.route import sio
from src.models import SensorData, NonWorkingSensor
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schema import SensorDataRequest, SensorDataSchema
from src.schema import FeatureData
from typing import Optional


import numpy as np
from src.services.user import get_current_user, get_admin_user
from src.services.sensor import (
    create_sensordata,
    get_sensordata as get_sensordate_from_db,
    get_last_sensordata as get_last_sensordata_from_db,
    get_sensordata_by_id as get_sensordata_by_id_from_db,
    purge_sensordata as purge_sensordata_fro_db,
    get_non_working_sensors as get_non_working_sensors_from_db,
    purge_sensordata_by_date as purge_sensordata_by_date_from_db,
    get_sensordata_by_date as get_sensordata_by_date_from_db,
)


system_router = APIRouter(prefix="/system", tags=["System Operations"])


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

        result = await create_sensordata(db, db_item)

        try:
            await sio.emit(
                "sensor_data", SensorDataSchema.model_validate(result).model_dump()
            )
        except Exception as e:
            print(f"Error emitting sensor data: {e}")

        return {"results": db_item}
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@system_router.get("/get_sensordata")
async def get_sensordata(
    db: AsyncSession = Depends(get_db),
    auth=Depends(get_current_user),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 10,
):
    """
    Purge sensor data between start_date and end_date (inclusive).
    Dates must be in ISO 8601 format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.
    """
    if page < 1 or page_size < 1:
        raise HTTPException(
            status_code=400, detail="Page and page_size must be greater than 0"
        )

    offset = (page - 1) * page_size

    if start_date and end_date:
        result = await get_sensordata_by_date_from_db(db, start_date, end_date)
    elif start_date or end_date:
        raise HTTPException(
            status_code=400,
            detail="Both start_date and end_date must be provided together.",
        )
    else:
        result = await get_sensordate_from_db(db, offset, page_size)

    return {"results": result}


@system_router.get("/get_sensordata/last")
async def get_last_sensordata(
    db: AsyncSession = Depends(get_db), auth=Depends(get_current_user)
):
    result = await get_last_sensordata_from_db(db)

    if not result:
        raise HTTPException(status_code=404, detail="Sensor data not found")

    return {"results": result}


@system_router.get("/get_sensordata/{id}")
async def get_sensordata_by_id(
    id: int, db: AsyncSession = Depends(get_db), auth=Depends(get_current_user)
):
    result = await get_sensordata_by_id_from_db(db, id)

    if not result:
        raise HTTPException(status_code=404, detail="Sensor data not found")

    return {"results": result}


@system_router.delete("/sensordata/purge")
async def purge_sensordata(
    db: AsyncSession = Depends(get_db), admin_user: str = Depends(get_admin_user)
):
    await purge_sensordata_fro_db(db)
    return {"message": "Sensor data purged successfully"}


@system_router.get("/non_working_sensors")
async def get_non_working_sensors(
    db: AsyncSession = Depends(get_db), auth=Depends(get_current_user)
):
    result = await get_non_working_sensors_from_db(db)

    return {"results": result}


@system_router.delete("/sensordata/purge-by-date")
async def purge_sensordata_by_date(
    start_date: str,
    end_date: str,
    db: AsyncSession = Depends(get_db),
    admin_user: str = Depends(get_admin_user),
):
    """
    Purge sensor data between start_date and end_date (inclusive).
    Dates must be in ISO 8601 format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.
    """
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use ISO 8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS).",
        )

    try:
        await purge_sensordata_by_date_from_db(db, start_dt, end_dt)
        return {"message": "Sensor data purged successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error purging sensor data: {str(e)}"
        )
