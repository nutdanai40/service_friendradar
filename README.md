# FriendRadar Services

Backend services for the FriendRadar application, organizing Face Recognition and Chat features.

## Project Structure

- **`face_service/`**: Face Recognition API (FastAPI)
- **`chat_service/`**: Real-time Chat API (FastAPI + WebSockets)
- **`models/`**: AI Models (YuNet, SFace)
- **`web_client/`**: Simple HTML/JS Client for testing
- **`legacy/`**: Archived old files

## Prerequisites

- Python 3.8+
- Dependencies: `pip install -r requirements.txt`

## 🚀 How to Run

### 1. Face Recognition Service
Runs on port **8001**.

```bash
cd face_service
python3 main.py
```
- Stats: http://localhost:8001/
- Docs: http://localhost:8001/docs

### 2. Chat Service
Runs on port **8002**.

```bash
cd chat_service
python3 main.py
```
- Websocket: `ws://localhost:8002/api/v1/chat/ws/{username}`

## 🧪 Testing with Web Client
Open `web_client/chat.html` in your browser to test the chat functionality.
