from fastapi import APIRouter, HTTPException, Depends
from app.core.database import SessionLocal
from app.models.models import Offer, UserProfile
from app.tasks.scraping import scrape_linkedin_task
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/scraping", tags=["scraping"])


@router.post("/trigger/{user_id}")
def trigger_scraping(user_id: int, current_user: User = Depends(get_current_user)):
    """Manually trigger a LinkedIn scraping task for the given user."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to trigger scraping for this user")
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
    finally:
        db.close()

    task = scrape_linkedin_task.delay(user_id)
    return {"message": "Scraping task triggered", "task_id": task.id}


@router.get("/offers/{user_id}")
def get_offers(user_id: int, current_user: User = Depends(get_current_user)):
    """Return all scraped offers from MySQL."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access offers for this user")
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")

        offers = db.query(Offer).filter(Offer.user_id == user_id).all()
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


