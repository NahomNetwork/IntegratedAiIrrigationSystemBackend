from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from src.routes.socketio.route import sio
from src.models import SensorData, NonWorkingSensor
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.routes.response_model import SensorDataRequest
from sqlalchemy.future import select

system_router = APIRouter(prefix="/system")


@system_router.post("/sensor_data")
async def receive_sensordata(
    req: SensorDataRequest, db: AsyncSession = Depends(get_db)
):
    sensor_data_dict = req.model_dump()
    await sio.emit("sensor_data", sensor_data_dict)

    # model prediction happens here

    non_working_sensors_data = sensor_data_dict.pop("Non_working_sensors", [])
    number_of_working_sensors = sensor_data_dict.pop("working_sensors", 0)
    db_item = SensorData(
        **sensor_data_dict,
        non_working_sensors=[
            NonWorkingSensor(sensor_name=item) for item in non_working_sensors_data
        ],
    )

    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)

    # engine = request.app.state.faiss_engine
    # if not engine:
    #     return HTTPException(status_code=503, detail="FAISS engine not initialized")

    return {"results": db_item}


@system_router.get("/get_sensordata")
async def get_sensordata(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SensorData).offset(0).limit(10))
    data = result.scalars().all()

    return {"results": data}


@system_router.get("/get_sensordata/{id}")
async def get_sensordata_by_id(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SensorData).where(SensorData.id == id))
    data = result.scalars().first()

    if not data:
        raise HTTPException(status_code=404, detail="Sensor data not found")

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


@system_router.delete("/sensordata/purge")
async def purge_sensordata(db: AsyncSession = Depends(get_db)):
    await db.execute("TRUNCATE TABLE sensordata")
    await db.commit()
    return {"message": "Sensor data purged successfully"}


@system_router.get("/non_working_sensors")
async def get_non_working_sensors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NonWorkingSensor))
    data = result.scalars().all()

    return {"results": data}


@system_router.get("/sensordata/purge-by-date")
async def purge_sensordata_by_date(
    start_date: str, end_date: str, db: AsyncSession = Depends(get_db)
):
    await db.execute(
        "DELETE FROM sensordata WHERE received_at BETWEEN :start_date AND :end_date",
        {"start_date": start_date, "end_date": end_date},
    )
    await db.commit()
    return {"message": "Sensor data purged successfully"}
