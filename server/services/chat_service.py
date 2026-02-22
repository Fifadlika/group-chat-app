from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        # dict: saves active connections
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[username] = websocket
        print(f"[+] {username} connected. Total: {len(self.active_connections)} user")

    def disconnect(self, username: str):
        if username in self.active_connections:
            del self.active_connections[username]
            print(f"[-] {username} disconnected. Total: {len(self.active_connections)} user")

    async def broadcast(self, message: dict, sender: str):
        disconnected = []

        for username, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(username)

        for username in disconnected:
            self.disconnect(username)

    async def send_to_user(self, username: str, message: dict):
        if username in self.active_connections:
            await self.active_connections[username].send_json(message)

manager = ConnectionManager()
