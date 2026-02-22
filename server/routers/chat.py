from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.dependencies import verify_websocket_token, get_current_user
from services.chat_service import manager
from services.message_service import save_message, get_recent_messages

router = APIRouter()

@router.get("/messages")
def get_messages(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    REST endpoint to retrieve chat history.
    """
    messages = get_recent_messages(db)
    return [
        {
            "type": "message",
            "username": msg.username,
            "message": msg.content,
            "timestamp": msg.timestamp.strftime("%H:%M")
        }
        for msg in messages
    ]

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

    await manager.send_to_user(username, {
        "type": "online_users",
        "users": manager.get_online_users(),
        "timestamp": manager.get_timestamp(),
    })

    await manager.broadcast({
        "type": "system",
        "username": "System",
        "message": f"{username} has joined the chat",
        "timestamp":manager.get_timestamp(),
    }, sender=username)

    try:
        while True:
            data = await websocket.receive_json()
            message_text = data.get("message", "").strip()           
            
            if not message_text:
                continue

            await manager.broadcast({
                "type": "message",
                "username": username,
                "message": data.get("message", ""),
                "timestamp": manager.get_timestamp(),
            }, sender=username)

    except WebSocketDisconnect:
        manager.disconnect(username)
        await manager.broadcast({
            "type": "system",
            "username": "System",
            "message": f"{username} has left the chat",
            "timestamp": manager.get_timestamp(),
        }, sender=username)