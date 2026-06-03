from fastapi import APIRouter, HTTPException
from app.core.database import SessionLocal
from app.models.models import Offer, UserProfile
from app.tasks.scraping import scrape_linkedin_task

router = APIRouter(prefix="/api/scraping", tags=["scraping"])


@router.post("/trigger/{user_id}")
def trigger_scraping(user_id: int):
    """Manually trigger a LinkedIn scraping task for the given user."""
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
    finally:
        db.close()

    task = scrape_linkedin_task.delay(user_id)
    return {"message": "Scraping task triggered", "task_id": task.id}


@router.get("/offers/{user_id}")
def get_offers(user_id: int):
    """Return all scraped offers from MySQL."""
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")

        offers = db.query(Offer).all()
        return [
            {
                "id": o.id,
                "title": o.title,
                "company": o.company,
                "location": o.location,
                "url": o.url,
                "source": o.source,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in offers
        ]
    finally:
        db.close()
