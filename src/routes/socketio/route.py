import socketio
from src.services.user import get_current_user

# Create a shared Socket.IO server instance
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


# Register event handlers
@sio.event
async def connect(sid, environ, auth):
    token = auth.get("token") if auth else None
    if not token:
        print(f"Connection attempt without token from {sid}")
        return False
    user = await get_current_user(token)
    if not user:
        print(f"Invalid token for {sid}")
        return False
    print(f"Client connected: {sid}")
    await sio.save_session(sid, {"user": user.username})


@sio.event
async def disconnect(sid):
    session = await sio.get_session(sid)
    print(f"{session['user']} disconnected")
