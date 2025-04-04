from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Header

app = FastAPI()
rooms = {}
CONNECT_TOKEN = "Bearer ZAa3HejENjhl5G45qTSePv4R0KHzKqO_ZTAUCU"
SEND_TOKEN = "Bearer WunI9tEpaMEz36yx8Qhs7CMMerrwEn4HeWKHnvruRx"

@app.websocket("/ws/{room}")
async def websocket_endpoint(ws: WebSocket, room: str, authorization: str = Header(None)):
    if authorization != CONNECT_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
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
async def send_message(room: str, request: dict, authorization: str = Header(None)):
    if authorization != SEND_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if room not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    for ws in rooms[room].copy():
        try:
            await ws.send_json(request)
        except:
            rooms[room].discard(ws)
    return {"status": "Message sent"}

@app.get("/ping")
async def ping():
    return {"status": "alive"}
