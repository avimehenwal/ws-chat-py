from fastapi import FastAPI
from health.routes import health_router
from joke.routes import joke_router

app = FastAPI()

app.include_router(health_router)
app.include_router(joke_router)
