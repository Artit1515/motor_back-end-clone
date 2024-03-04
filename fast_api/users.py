import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from database import db

class Register(BaseModel):
    user_id: str = str(uuid.uuid4())
    username: str
    email: str
    passwd: str
    motor_owned: list = []
    create_on: datetime = datetime.now()
    
class Login(BaseModel):
    email: str
    passwd: str

class UserConfig(BaseModel):
    username: str
    password: str
    update_on: datetime = datetime.now()
    
class AddMotor(BaseModel):
    user_id: str
    motor_id: str
    motor_name: str
    
router = APIRouter()
user_coll = db.collection("users")

@router.get("/")
async def hello_user():
    return { "msg": "FastAPI user"}

@router.post("/register")
async def register(user: Register):
    user_coll.insert_one(user.model_dump())
    return {"msg": "User added"}

@router.post("/login")
async def login(user: Login):
    usr = user_coll.find_one(user.model_dump())
    if usr :
        return { "msg": "Logged in successfully." }
    else:
        raise HTTPException(status_code=404)
    
@router.post("/add/motor")
async def add_motor_owned(info: AddMotor):
    try:
        user = user_coll.find_one({"user_id": info.user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        motor_info = {
            "motor_id": info.motor_id,
            "motor_name": info.motor_name
        }
        user_coll.update_one(
            {"user_id": info.user_id},
            {"$push": {"motor_owned": motor_info}}
        )
        return {"msg": "Motor added successfully", "motor_id": info.motor_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
