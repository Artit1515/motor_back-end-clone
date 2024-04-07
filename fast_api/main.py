from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from users import router as users_router
from devices import router as devices_router
from database import db

app = FastAPI()

# Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#Root greeting
@app.get("/")
async def root():
    return {"message": "Hello API"}
 
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(devices_router, prefix="/devices", tags=["devices"])