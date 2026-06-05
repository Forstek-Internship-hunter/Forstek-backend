from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
from app.core.database import SessionLocal
from app.models.models import Application, Offer

router = APIRouter(prefix="/api/applications", tags=["applications"])


class StatusUpdate(BaseModel):
    status: Literal["pending", "sent", "rejected", "accepted"]


@router.get("/{user_id}")
def get_applications(user_id: int):
    """Return all applications with offer details joined."""
    db = SessionLocal()
    try:
        results = (
            db.query(Application, Offer)
            .join(Offer, Application.offer_id == Offer.id)
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
def update_application_status(app_id: int, body: StatusUpdate):
    """Update the status of an application."""
    db = SessionLocal()
    try:
        application = db.query(Application).filter(Application.id == app_id).first()
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        application.status = body.status
        db.commit()
        return {
            "id": application.id,
            "status": application.status,
            "message": "Status updated successfully",
        }
    finally:
        db.close()
