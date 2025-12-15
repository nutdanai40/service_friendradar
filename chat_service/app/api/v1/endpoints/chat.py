from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.chat_service import ConnectionManager
from datetime import datetime
import json

router = APIRouter()
manager = ConnectionManager()

@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    """WebSocket endpoint for chat"""
    await manager.connect(websocket, username)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Broadcast message to all users
            await manager.broadcast({
                "type": "message",
                "username": username,
                "content": message_data.get("content", ""),
                "timestamp": datetime.now().isoformat(),
                "users": list(manager.active_connections.keys())
            })
            
    except WebSocketDisconnect:
        manager.disconnect(username)
        # Notify all users about user leaving
        await manager.broadcast({
            "type": "leave",
            "username": username,
            "content": f"{username} left the chat",
            "timestamp": datetime.now().isoformat(),
            "users": list(manager.active_connections.keys())
        })
