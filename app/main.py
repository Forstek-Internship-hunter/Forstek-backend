from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine
from app.models.models import Base
from app.api.scraping import router as scraping_router
from app.api.applications import router as applications_router
from app.tasks.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="Forstek API", lifespan=lifespan)

app.include_router(scraping_router)
app.include_router(applications_router)


@app.get("/")
def root():
    return {"message": "Forstek API is running 🚀"}