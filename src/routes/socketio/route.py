import socketio

# Create a shared Socket.IO server instance
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


# Register event handlers
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.event
async def message(sid, data):
    print(f"Message from {sid}: {data}")
    await sio.emit("response", {"data": f"Echo: {data}"}, to=sid)
