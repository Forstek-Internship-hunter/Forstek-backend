from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine
from app.models.models import Base
from app.api.scraping import router as scraping_router
from app.api.applications import router as applications_router
from app.api.experiences import router as experiences_router
from app.api.auth import router as auth_router
from app.api.profile import router as profile_router
from app.tasks.scheduler import start_scheduler, stop_scheduler



@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Forstek API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(scraping_router)
app.include_router(applications_router)
app.include_router(experiences_router)
app.include_router(auth_router)
app.include_router(profile_router)



@app.get("/")
def root():
    return {"message": "Forstek API is running 🚀"}