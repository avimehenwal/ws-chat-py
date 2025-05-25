import asyncio
import random
from typing import List
from fastapi import APIRouter
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from joke.data import JOKES

chat_router = APIRouter(prefix="/chat", tags=["Chat API"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accepts a new WebSocket connection and adds it to the active connections."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New WebSocket connection established: {websocket.client}")

    def disconnect(self, websocket: WebSocket):
        """Removes a WebSocket connection from the active connections."""
        self.active_connections.remove(websocket)
        print(f"WebSocket connection disconnected: {websocket.client}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Sends a message to a specific WebSocket client."""
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        """Sends a message to all active WebSocket clients."""
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


async def send_jokes_periodically(websocket: WebSocket):
    """
    Sends a random joke to the connected WebSocket client every 5 seconds asynchronsouly
    """
    try:
        while True:
            joke = random.choice(JOKES)
            await manager.send_personal_message(f"Joke: {joke}", websocket)
            await asyncio.sleep(0.2) # 200ms
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Error in joke sending task for client {websocket.client}: {e}")


@chat_router.get("/")
def get_chat_service_status():
    return {"Status": "Chat enabled", "time": datetime.now().isoformat()}


@chat_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    joke_task = asyncio.create_task(send_jokes_periodically(websocket))

    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You: {data}", websocket)
            await manager.broadcast(
                f"Client {websocket.client.host}:{websocket.client.port} says: {data}"
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        joke_task.cancel()
        await manager.broadcast(
            f"Client {websocket.client.host}:{websocket.client.port} has left the chat."
        )

    except Exception as e:
        print(f"WebSocket error for client {websocket.client}: {e}")
        manager.disconnect(websocket)
        joke_task.cancel()
        await manager.broadcast(
            f"Client {websocket.client.host}:{websocket.client.port} encountered an error and disconnected."
        )
