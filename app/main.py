from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

app = FastAPI()
rooms = {}

class MessageRequest(BaseModel):
    input: str

@app.websocket("/ws/{room}")
async def websocket_endpoint(ws: WebSocket, room: str):
    await ws.accept()
    rooms.setdefault(room, set()).add(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        rooms[room].discard(ws)
        if not rooms[room]: 
            del rooms[room]

@app.post("/send/{room}")
async def send_message(room: str, request: MessageRequest):
    if room not in rooms:
        raise HTTPException(404, "Room not found")
    for ws in rooms[room].copy():
        try:
            await ws.send_text(request.input)
        except:
            rooms[room].discard(ws)
    return {"status": "Message sent"}
