from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Literal
from app.core.database import SessionLocal
from app.models.models import UserExperience, UserProfile
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/experiences", tags=["experiences"])


class ExperienceCreate(BaseModel):
    type: Literal["academic", "professional", "project", "certification"]
    title: str
    institution: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@router.post("/{user_id}")
def add_experience(user_id: int, body: ExperienceCreate, current_user: User = Depends(get_current_user)):
    """Add a new experience for a user."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to add experience for this user")
        
    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")

        experience = UserExperience(
            user_id=user_id,
            type=body.type,
            title=body.title,
            institution=body.institution,
            description=body.description,
            start_date=body.start_date,
            end_date=body.end_date,
        )
        db.add(experience)
        db.commit()
        db.refresh(experience)
        return {
            "id": experience.id,
            "user_id": experience.user_id,
            "type": experience.type,
            "title": experience.title,
            "institution": experience.institution,
            "description": experience.description,
            "start_date": experience.start_date,
            "end_date": experience.end_date,
            "message": "Experience added successfully",
        }
    finally:
        db.close()


@router.get("/{user_id}")
def get_experiences(user_id: int, current_user: User = Depends(get_current_user)):
    """Get all experiences for a user."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access experiences for this user")

    db = SessionLocal()
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")

        experiences = (
            db.query(UserExperience)
            .filter(UserExperience.user_id == user_id)
            .order_by(UserExperience.start_date.desc())
            .all()
        )
        return [
            {
                "id": exp.id,
                "user_id": exp.user_id,
                "type": exp.type,
                "title": exp.title,
                "institution": exp.institution,
                "description": exp.description,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "created_at": exp.created_at.isoformat() if exp.created_at else None,
            }
            for exp in experiences
        ]
    finally:
        db.close()


@router.delete("/{exp_id}")
def delete_experience(exp_id: int, current_user: User = Depends(get_current_user)):
    """Delete an experience by ID."""
    db = SessionLocal()
    try:
        experience = db.query(UserExperience).filter(UserExperience.id == exp_id).first()
        if not experience:
            raise HTTPException(status_code=404, detail="Experience not found")

        if experience.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this experience")

        db.delete(experience)
        db.commit()
        return {"message": "Experience deleted successfully", "id": exp_id}
    finally:
        db.close()
