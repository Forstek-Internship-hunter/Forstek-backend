from fastapi import FastAPI
from app.core.database import engine
from app.models.models import Base
app = FastAPI(title="Forstek API")

@app.get("/")
def root():
    return {"message": "Forstek API is running 🚀"}