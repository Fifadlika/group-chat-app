from fastapi import Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordBearer
from core.security import decode_access_token, is_token_blacklisted

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token is invalid, please relogin."
        )
    
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Token is either invalid or expired."
        )
    
    return payload

async def verify_websocket_token(websocket: WebSocket) -> str | None:
    """
    Retrieve and verify JWT token from WebSocket query parameter.
    
    Client connects to : ws://localhost:8000/ws/chat?token=<jwt_token>
    """
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        return None

    if is_token_blacklisted(token):
        await websocket.close(code=1008)
        return None

    payload = decode_access_token(token)
    if payload is None:
        await websocket.close(code=1008)
        return None

    username = payload.get("sub")
    if not username:
        await websocket.close(code=1008)
        return None

    return username
