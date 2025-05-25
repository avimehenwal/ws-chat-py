import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from health.routes import health_router
from joke.routes import joke_router
from chat.routes import chat_router
from www.routes import www_router

app = FastAPI(
    title="WebSocket Chat API",
    description="A simple FastAPI application with WebSocket chat, health, and joke endpoints.",
    version="1.0.0",
)

current_dir = os.path.dirname(os.path.abspath(__file__))
app.mount(
    "/public",
    StaticFiles(directory=os.path.join(current_dir, "www", "static")),
    name="public",
)

app.include_router(health_router)
app.include_router(joke_router)
app.include_router(chat_router)
app.include_router(www_router)
