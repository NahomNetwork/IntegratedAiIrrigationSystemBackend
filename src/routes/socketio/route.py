import socketio
from src.services.user import verify_token
from urllib.parse import parse_qs

# Create a shared Socket.IO server instance
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


# Register event handlers
@sio.event
async def connect(sid, environ, auth):
    token_auth = auth.get("token") if auth else None
    token_query = environ.get("QUERY_STRING", "")

    token = token_auth or parse_qs(token_query).get("token", [None])[0]
    if not token:
        print(f"Connection attempt without token from {sid}")
        return False
    user = verify_token(token)
    if not user:
        print(f"Invalid token for {sid}")
        return False
    print(f"Client connected: {sid}")
    await sio.save_session(sid, {"user": user.get("sub", "unknown")})


@sio.event
async def disconnect(sid):
    session = await sio.get_session(sid)
    print(f"{session['user']} disconnected")
