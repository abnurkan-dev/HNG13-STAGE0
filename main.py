from fastapi import FastAPI
from controller import country_controller
from core.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
import logging
import uvicorn


app = FastAPI(title="Country currency and Backend API", version="1.0.0")

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

# Register routers
app.include_router(country_controller.router)


# Attempt to connect to DB safely
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database schema synchronized.")


@app.get("/")
def root():
    return {"message": "Welcome to the Country currency and Backend API"}


# @app.get("/status")
# def get_status():
#     from sqlalchemy import func
#     from core.database import SessionLocal
#     db = SessionLocal()
#     total = db.query(func.count()).select_from(Base.metadata.tables['countries']).scalar()
#     latest = db.query(func.max(Base.metadata.tables['countries'].c.last_refreshed_at)).scalar()
#     db.close()
#     return {"total_countries": total or 0, "last_refreshed_at": str(latest) if latest else None}

   
# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))  # PXXL sets this automatically
    uvicorn.run("main:app", host="0.0.0.0", port=port)