import asyncio
from typing import Dict
from fastapi import WebSocket
from datetime import datetime, timedelta
import redis.asyncio as redis


class ConnectionManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.ws_to_client_id: Dict[WebSocket, str] = {}

        self.TOTAL_CLOSED_CONNECTIONS_KEY = "chat_metrics:total_closed_connections"
        self.TOTAL_CONNECTION_DURATION_KEY = (
            "chat_metrics:total_connection_duration_seconds"
        )
        self.ACTIVE_CONNECTIONS_SET_KEY = "chat_metrics:active_connections_set"

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        client_id = f"{websocket.client.host}:{websocket.client.port}"
        self.ws_to_client_id[websocket] = client_id

        connection_data = {
            "connect_time": datetime.now().isoformat(),
            "messages_sent": 0,
            "messages_received": 0,
            "client_host": websocket.client.host,
            "client_port": websocket.client.port,
        }
        await self.redis_client.hset(f"chat_conn:{client_id}", mapping=connection_data)
        await self.redis_client.sadd(self.ACTIVE_CONNECTIONS_SET_KEY, client_id)

        print(
            f"Client {client_id} connected. Total active (Redis): {await self.redis_client.scard(self.ACTIVE_CONNECTIONS_SET_KEY)}"
        )

    async def disconnect(self, websocket: WebSocket):
        client_id = self.ws_to_client_id.pop(websocket, None)
        if client_id:
            await self.redis_client.srem(self.ACTIVE_CONNECTIONS_SET_KEY, client_id)

            connection_data = await self.redis_client.hgetall(f"chat_conn:{client_id}")
            if connection_data:
                connect_time_str = connection_data.get("connect_time")
                if connect_time_str:
                    connect_time = datetime.fromisoformat(connect_time_str)
                    disconnect_time = datetime.now()
                    duration_seconds = (disconnect_time - connect_time).total_seconds()

                    await self.redis_client.incr(self.TOTAL_CLOSED_CONNECTIONS_KEY)
                    await self.redis_client.incrbyfloat(
                        self.TOTAL_CONNECTION_DURATION_KEY, duration_seconds
                    )

                await self.redis_client.delete(f"chat_conn:{client_id}")

            print(
                f"Client {client_id} disconnected. Total active (Redis): {await self.redis_client.scard(self.ACTIVE_CONNECTIONS_SET_KEY)}"
            )

    async def send_personal_message(self, message: str, websocket: WebSocket):
        client_id = self.ws_to_client_id.get(websocket)
        if client_id:
            try:
                await websocket.send_text(message)
                await self.redis_client.hincrby(
                    f"chat_conn:{client_id}", "messages_sent", 1
                )
            except Exception as e:
                print(f"Error sending message to {client_id}: {e}")
                await self.disconnect(websocket)

    async def broadcast(self, message: str):
        active_client_ids = await self.redis_client.smembers(
            self.ACTIVE_CONNECTIONS_SET_KEY
        )
        for ws, client_id in list(self.ws_to_client_id.items()):
            if client_id in active_client_ids:
                try:
                    await ws.send_text(message)
                    await self.redis_client.hincrby(
                        f"chat_conn:{client_id}", "messages_sent", 1
                    )
                except Exception as e:
                    print(f"Error broadcasting to {client_id}: {e}")
                    await self.disconnect(ws)

    async def increment_messages_received(self, websocket: WebSocket):
        client_id = self.ws_to_client_id.get(websocket)
        if client_id:
            await self.redis_client.hincrby(
                f"chat_conn:{client_id}", "messages_received", 1
            )

    async def get_metrics(self):
        total_open_connections = await self.redis_client.scard(
            self.ACTIVE_CONNECTIONS_SET_KEY
        )
        total_closed_connections = int(
            await self.redis_client.get(self.TOTAL_CLOSED_CONNECTIONS_KEY) or 0
        )
        total_connection_duration_seconds = float(
            await self.redis_client.get(self.TOTAL_CONNECTION_DURATION_KEY) or 0.0
        )

        avg_closed_duration_seconds = (
            (total_connection_duration_seconds / total_closed_connections)
            if total_closed_connections > 0
            else 0.0
        )

        active_connection_details = []
        active_client_ids = await self.redis_client.smembers(
            self.ACTIVE_CONNECTIONS_SET_KEY
        )

        for client_id in active_client_ids:
            conn_data = await self.redis_client.hgetall(f"chat_conn:{client_id}")
            if conn_data:
                connect_time_str = conn_data.get("connect_time")
                current_duration_seconds = 0.0
                if connect_time_str:
                    connect_time = datetime.fromisoformat(connect_time_str)
                    current_duration_seconds = (
                        datetime.now() - connect_time
                    ).total_seconds()

                active_connection_details.append(
                    {
                        "client": client_id,
                        "connected_since": conn_data.get("connect_time"),
                        "current_duration_seconds": round(current_duration_seconds, 2),
                        "messages_sent": int(conn_data.get("messages_sent", 0)),
                        "messages_received": int(conn_data.get("messages_received", 0)),
                    }
                )

        return {
            "total_open_connections": total_open_connections,
            "total_closed_connections": total_closed_connections,
            "total_connection_duration_seconds": round(
                total_connection_duration_seconds, 2
            ),
            "average_closed_connection_duration_seconds": round(
                avg_closed_duration_seconds, 2
            ),
            "active_connections_details": active_connection_details,
        }
