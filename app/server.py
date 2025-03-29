from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException

app = FastAPI()
rooms = {}

@app.websocket("/ws/{room}")
async def websocket_endpoint(ws: WebSocket, room: str):
    await ws.accept()
    rooms.setdefault(room, set()).add(ws)
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect:
        rooms[room].discard(ws)
        if not rooms[room]: del rooms[room]

@app.post("/send/{room}")
async def send_message(room: str, message: str):
    if room not in rooms: raise HTTPException(404, "Room not found")
    for ws in rooms[room].copy():
        try: await ws.send_text(message)
        except: rooms[room].discard(ws)
    return {"status": "Message sent"}
