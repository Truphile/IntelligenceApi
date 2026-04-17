from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from app.api.routes import profileRoutes
from app.data.respository.profileDatabase import init_db, close_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting Profile Intelligence Service...")
    await init_db()
    yield
    logger.info("Shutting down...")
    await close_db()


app = FastAPI(
    title="Profile Intelligence Service",
    description="Enriches names with data from multiple external APIs",
    version="2.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(profileRoutes.router ,prefix="/api", tags=["profiles"])


@app.get("/")
async def health_check():
    return {"status": "OK", "service": "Profile Intelligence Service", "version": "2.0.0"}



if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)