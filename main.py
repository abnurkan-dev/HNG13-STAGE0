from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn

from fastapi import FastAPI, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from api.routes_profile import router as profile_router
import redis.asyncio as redis
from contextlib import asynccontextmanager


# Initialize app
app = FastAPI(title="Profile API with MVC Architecture", version="1.0.0")


# ✅ optional flag to disable rate limiter globally
rate_limiter_enabled = True
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(profile_router)

#@app.get("/",dependencies=[Depends(RateLimiter(times=5, seconds=60))])
@app.get("/", dependencies=[Depends(RateLimiter(times=5, seconds=60))] if rate_limiter_enabled else [])
async def root():
    return {"message": "Welcome to the Profile API"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global rate_limiter_enabled
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    try:
        r = await redis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            ssl=REDIS_URL.startswith("rediss://")  # Upstash uses SSL
        )
        await FastAPILimiter.init(r)
        rate_limiter_enabled = True
        print("✅ Connected to Upstash Redis successfully — rate limiting enabled")

        logger.info("✅ Connected to Redis for rate limiting")
        logger.info("🚀 FastAPI is running at: http://127.0.0.1:8000")
        logger.info("📘 Docs available at: http://127.0.0.1:8000/docs")
        logger.info("🔗 Profile endpoint: http://127.0.0.1:8000/me")
    
    
    except Exception as e:
        rate_limiter_enabled = False
        print(f"⚠️ Redis connection failed: {e}")
        print("➡️ Proceeding without rate limiting.")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
