from pydantic import BaseModel
from datetime import datetime, timedelta
from auth import tz
class Register(BaseModel):
    user_id: str = ""
    username: str
    email: str
    passwd: str
    role: str = "customer"
    create_on: datetime = datetime.now(tz=tz)
    motor_owned: list = []
    
class Login(BaseModel):
    email: str
    passwd: str
    
class User_id(BaseModel):
    user_id: str