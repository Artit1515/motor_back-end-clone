from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from database import db

class IoT_Recv(BaseModel): # Data that sent by MQTT.
    motor_id: str
    temperature: float
    vibration: float
    voltage: float
    current: float
    rpm: float
    timestamp: datetime = datetime.now()

class Sensors(BaseModel): # Model for only sensors that will be call from web-app.
    temperature: float
    vibration: float
    voltage: float
    current: float
    rpm: float
    timestamp: datetime = datetime.now()

class Motor_data(BaseModel):
    motor_id: str
    sensors: list = []

class Motor_info(BaseModel):
    motor_id: str
    motor_name: str
    location: str
    series: str
    department: str
    create_on: datetime = datetime.now()

class Motor_id(BaseModel):
    motor_id: str

router = APIRouter()
motor_data_coll = db.collection("motor_data")
motor_info_coll = db.collection("motor_info")

@router.get("/")
async def hello_devices():
    return { "msg": "Device Router!"}

#___ Motor Info ___
@router.post("/motor/add")
async def add_motor(motor_info: Motor_info):
    motor_info_coll.insert_one(motor_info.model_dump())
    return { "msg": "Motor added." }

@router.post("/motor/find")
async def find_motor(mt_data: Motor_id):
    motor = motor_info_coll.find_one(mt_data.model_dump())
    if motor :
        return {"msg": "Found your motor",
                "data": motor }
    else:
        raise HTTPException(status_code=404)

@router.delete("/motor/delete")
async def delete_motor(motor_id: Motor_id):
    try:
        motor = motor_info_coll.find_one(motor_id.model_dump())
        if motor :
            motor_info_coll.delete_one(motor_id.model_dump())
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

###___ Motor Data / Sensor ___###

# Adding sensors data from esp
@router.post("/sensor/store")
async def store_data(mt_data: IoT_Recv):
    sensor = {
        "temperature": mt_data.temperature,
        "vibration": mt_data.vibration,
        "voltage": mt_data.voltage,
        "current": mt_data.current,
        "rpm": mt_data.rpm,
        "timestamp": datetime.now()
    }
    motor_exist = motor_data_coll.find_one({"motor_id":mt_data.motor_id})
    if motor_exist:
        ft = {"motor_id": mt_data.motor_id}
        update = {"$push": {"sensors": sensor}}
        motor_data_coll.update_one(ft,update=update, upsert=True) #push new data to sensors array
        return { "msg": "Added new data." }
    else:
        motor = {
            "motor_id": mt_data.motor_id,
            "sensors": [sensor] #create array with first sensors data
        }
        motor_data_coll.insert_one(motor)
        return { "msg": "Stored data to database." }

# Getting sensors data from web-app
@router.post("/get/motor_data")
async def get_motor_data(motor_id: Motor_id):
    motor = motor_data_coll.find_one(motor_id.model_dump())
    if motor:
        sensors = [Sensors(**sensor) for sensor in motor["sensors"]]
        return { "motor_id": motor["motor_id"],
                "data": sensors}
    else:
        return { "msg": "Motor not found." }
    