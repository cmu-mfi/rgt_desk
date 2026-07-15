from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router
from process_monitor import process_monitor

@asynccontextmanager
async def lifespan(app: FastAPI):
    process_monitor.start()
    yield
    process_monitor.stop()

app = FastAPI(lifespan=lifespan)

# CORS setup for Vue frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the API endpoints
app.include_router(router)
