from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Literal
from app.core.database import SessionLocal
from app.models.models import Application, Offer
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/applications", tags=["applications"])


class StatusUpdate(BaseModel):
    status: Literal["pending", "sent", "rejected", "accepted"]


@router.get("/{user_id}")
def get_applications(user_id: int, current_user: User = Depends(get_current_user)):
    """Return all applications with offer details joined."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access applications for this user")
    db = SessionLocal()
    try:
        results = (
            db.query(Application, Offer)
            .join(Offer, Application.offer_id == Offer.id)
            .filter(Application.user_id == user_id)
            .all()
        )
        return [
            {
                "id": app.id,
                "status": app.status,
                "cover_letter": app.cover_letter,
                "created_at": app.created_at.isoformat() if app.created_at else None,
                "offer": {
                    "id": offer.id,
                    "title": offer.title,
                    "company": offer.company,
                    "location": offer.location,
                    "url": offer.url,
                    "source": offer.source,
                },
            }
            for app, offer in results
        ]
    finally:
        db.close()


@router.patch("/{app_id}/status")
def update_application_status(app_id: int, body: StatusUpdate, current_user: User = Depends(get_current_user)):
    """Update the status of an application."""
    db = SessionLocal()
    try:
        application = db.query(Application).filter(Application.id == app_id).first()
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        if application.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this application")

        application.status = body.status
        db.commit()
        return {
            "id": application.id,
            "status": application.status,
            "message": "Status updated successfully",
        }
    finally:
        db.close()


