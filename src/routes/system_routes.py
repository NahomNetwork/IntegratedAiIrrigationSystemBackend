from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from src.routes.socketio.route import sio
from src.models import SensorData, NonWorkingSensor
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schema import SensorDataRequest
from src.schema import FeatureData

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
)


system_router = APIRouter(
    prefix="/system",
    tags=["System Operations"],
    dependencies=[Depends(get_current_user)],
)


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

        await sio.emit("sensor_data", result)

        return {"results": db_item}
    except Exception as e:
        raise HTTPException(500, detail=e)


@system_router.get("/get_sensordata")
async def get_sensordata(db: AsyncSession = Depends(get_db)):
    result = await get_sensordate_from_db(db)

    return {"results": result}


@system_router.get("/get_sensordata/last")
async def get_last_sensordata(db: AsyncSession = Depends(get_db)):
    result = await get_last_sensordata_from_db(db)

    if not result:
        raise HTTPException(status_code=404, detail="Sensor data not found")

    return {"results": result}


@system_router.get("/get_sensordata/{id}")
async def get_sensordata_by_id(id: int, db: AsyncSession = Depends(get_db)):
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
async def get_non_working_sensors(db: AsyncSession = Depends(get_db)):
    result = await get_non_working_sensors_from_db(db)

    return {"results": result}


@system_router.get("/sensordata/purge-by-date")
async def purge_sensordata_by_date(
    start_date: str,
    end_date: str,
    db: AsyncSession = Depends(get_db),
    admin_user: str = Depends(get_admin_user),
):
    await purge_sensordata_by_date_from_db(db, start_date, end_date)
    return {"message": "Sensor data purged successfully"}
