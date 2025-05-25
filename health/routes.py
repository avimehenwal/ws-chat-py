from fastapi import APIRouter
from datetime import datetime

health_router = APIRouter()


@health_router.get("/health")
def health_check():
    return {"Status": "Healthy", "time": datetime.now().isoformat()}
