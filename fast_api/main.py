import asyncio
import json
from fastapi import FastAPI, HTTPException
from bson import ObjectId, json_util
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pymongo.mongo_client import MongoClient #Import pymongo driver to connect mongodb
from typing import Optional
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
@app.get("/api")
async def root():
    return {"message": "Hello API"}
 
app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(devices_router, prefix="/devices", tags=["devices"])