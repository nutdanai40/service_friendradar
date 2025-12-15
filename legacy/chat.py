from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict
from datetime import datetime
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Store active connections: {username: websocket}
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, username: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[username] = websocket
        
        # Notify all users about new user
        await self.broadcast({
            "type": "join",
            "username": username,
            "content": f"{username} joined the chat",
            "timestamp": datetime.now().isoformat(),
            "users": list(self.active_connections.keys())
        })

    def disconnect(self, username: str):
        """Remove WebSocket connection"""
        if username in self.active_connections:
            del self.active_connections[username]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific user"""
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        """Send message to all connected users"""
        disconnected = []
        for username, connection in self.active_connections.items():
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(username)
        
        # Clean up disconnected users
        for username in disconnected:
            self.disconnect(username)

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
