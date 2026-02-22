from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.chat_service import manager

router = APIRouter()

@router.websocket("/ws/chat/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket, username)

    await manager.broadcast({
        "type": "system",
        "message": f"{username} has joined the chat",
        "username": "System"
    }, sender=username)

    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast({
                "type": "message",
                "username": username,
                "message": data.get("message", ""),
            }, sender=username)

    except WebSocketDisconnect:
        manager.disconnect(username)
        await manager.broadcast({
            "type": "system",
            "message": f"{username} has left the chat",
            "username": "System"
        }, sender=username)