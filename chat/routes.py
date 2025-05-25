import asyncio
import random
from typing import List
from fastapi import APIRouter
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from joke.data import JOKES # Assuming JOKES is accessible
from chat.connection_manager import ConnectionManager

chat_router = APIRouter(prefix="/chat", tags=["Chat API"])

# TODO: Get URL from env var
manager = ConnectionManager(redis_url="redis://localhost:6379")

async def send_jokes_periodically(websocket: WebSocket):
    try:
        while True:
            joke = random.choice(JOKES)
            await manager.send_personal_message(f"Joke: {joke}", websocket)
            await asyncio.sleep(0.2)  # 200ms
    except WebSocketDisconnect:
        pass
    except asyncio.CancelledError:
        print(f"Joke sending task for client {websocket.client} cancelled.")
    except Exception as e:
        print(f"Error in joke sending task for client {websocket.client}: {e}")

@chat_router.get("/")
def get_chat_service_status():
    return {"Status": "Chat enabled", "time": datetime.now().isoformat()}

@chat_router.get("/analytics")
async def get_chat_metrics():
    return await manager.get_metrics()

@chat_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    joke_task = asyncio.create_task(send_jokes_periodically(websocket))

    try:
        while True:
            data = await websocket.receive_text()
            await manager.increment_messages_received(websocket)

            if data == "GET_JOKE":
                joke = random.choice(JOKES)
                await manager.send_personal_message(f"Joke: {joke}", websocket)
            else:
                await manager.send_personal_message(f"You: {data}", websocket)
                await manager.broadcast(
                    f"Client {websocket.client.host}:{websocket.client.port} says: {data}"
                )

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        joke_task.cancel()
        await manager.broadcast(
            f"Client {websocket.client.host}:{websocket.client.port} has left the chat."
        )

    except Exception as e:
        print(f"WebSocket error for client {websocket.client}: {e}")
        await manager.disconnect(websocket)
        joke_task.cancel()
        await manager.broadcast(
            f"Client {websocket.client.host}:{websocket.client.port} encountered an error and disconnected."
        )
