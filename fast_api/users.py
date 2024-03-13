import uuid
import hashlib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from database import db
from devices import motor_data_coll, motor_info_coll

class Register(BaseModel):
    user_id: str = ""
    username: str
    email: str
    passwd: str
    role: str = "customer"
    create_on: datetime = datetime.now()
    motor_owned: list = []
    
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

class User_id(BaseModel):
    user_id: str
    
router = APIRouter()
user_coll = db.collection("users")

# Function to hash the password
def hash_password(password: str) -> str:
    algorithm = "sha256"
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(password.encode("utf-8"))
    hashed_password = hash_obj.hexdigest()
    return hashed_password

@router.get("/")
async def hello_user():
    return { "msg": "FastAPI user"}

@router.post("/register")
async def register(user: Register):
    user_exist = user_coll.find_one({"email": user.email})
    if user_exist:
        raise HTTPException(status_code=400, detail="Email already used.")
    #hash the password
    hashed_passwd = hash_password(user.passwd)
    user.passwd = hashed_passwd
    #assign user_id
    user_id = str(uuid.uuid4())
    user.user_id = user_id
    user_coll.insert_one(user.model_dump())
    return {"msg": "Registering successful."}

@router.post("/login")
async def login(user: Login):
    usr = user_coll.find_one({"email": user.email})
    if usr is None:
        raise HTTPException(status_code=404, detail="User not found.")
    
    hased_passwd = hash_password(user.passwd)
    if hased_passwd != usr["passwd"]:
        raise HTTPException(status_code=401, detail="Incorrect password.")
    return { "msg": "Logged in successfully.",
            "user":{
                "user_id": usr["user_id"],
                "username": usr["username"],
                "role": usr["role"],
                "motor_owned": usr["motor_owned"]
            }
        }

# Adding motor by customer
@router.post("/add/motor")
async def add_motor_owned(info: AddMotor):
    try:
        user = user_coll.find_one({"user_id": info.user_id})
        motor = motor_info_coll.find_one({"motor_id": info.motor_id})
        if (not user) or (not motor):
            raise HTTPException(status_code=404, detail="User or Motor not found")
        
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


@router.post("/get/user_data")
async def get_user_data(user_id: User_id):
    try:
        user = user_coll.find_one(user_id.model_dump())
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user["role"],
            "motor_owned": user["motor_owned"]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))