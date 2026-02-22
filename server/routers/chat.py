from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.chat_service import manager
from core.dependencies import verify_websocket_token

router = APIRouter()

@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """
    JWT-protected WebSocket endpoint.
    Client connects to: ws://localhost:8000/ws/chat?token=<jwt_token>
    """
    username = await verify_websocket_token(websocket)
    if username is None:
        return

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