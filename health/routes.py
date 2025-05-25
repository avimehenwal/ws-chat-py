from fastapi import APIRouter
from datetime import datetime

health_router = APIRouter(prefix="/health", tags=["Health API"])


@health_router.get("/")
def health_check():
    return {"Status": "Healthy", "time": datetime.now().isoformat()}
