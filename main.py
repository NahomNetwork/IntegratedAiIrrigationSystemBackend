from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.routes.api_route import api_route
from fastapi.middleware.cors import CORSMiddleware
import socketio
from src.routes.socketio.route import sio
from pathlib import Path
import sys
from src.model_handler import load_model

# Add the parent directory to the system path
sys.path.append(str(Path(__file__).resolve().parent.parent))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the Model Engine once when the app starts
    app.state.model = load_model()
    yield
    # Clean up resources when the app shuts down
    app.state.model = None


sio_app = socketio.ASGIApp(sio)


app = FastAPI(lifespan=lifespan)


app.mount("/socket.io", sio_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_route)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
