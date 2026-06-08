from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Literal
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.models import UserProfile, UserExperience

router = APIRouter(prefix="/api/profile", tags=["profile"])

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    speciality: Optional[str] = None
    skills: Optional[str] = None
    stage_type: Optional[str] = None
    location: Optional[str] = None
    languages: Optional[str] = None

class ExperienceCreate(BaseModel):
    type: Literal["academic", "professional", "project", "certification"]
    title: str
    institution: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

@router.get("")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        # Create one dynamically if it doesn't exist
        profile = UserProfile(
            user_id=current_user.id,
            name=current_user.full_name,
            speciality="",
            skills="",
            stage_type="",
            location="",
            languages=""
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("")
def update_profile(body: ProfileUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    if body.name is not None:
        profile.name = body.name
    if body.speciality is not None:
        profile.speciality = body.speciality
    if body.skills is not None:
        profile.skills = body.skills
    if body.stage_type is not None:
        profile.stage_type = body.stage_type
    if body.location is not None:
        profile.location = body.location
    if body.languages is not None:
        profile.languages = body.languages

    db.commit()
    db.refresh(profile)
    return profile

@router.get("/experiences")
def get_experiences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experiences = (
        db.query(UserExperience)
        .filter(UserExperience.user_id == current_user.id)
        .order_by(UserExperience.start_date.desc())
        .all()
    )
    return experiences

@router.post("/experiences")
def add_experience(body: ExperienceCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experience = UserExperience(
        user_id=current_user.id,
        type=body.type,
        title=body.title,
        institution=body.institution,
        description=body.description,
        start_date=body.start_date,
        end_date=body.end_date
    )
    db.add(experience)
    db.commit()
    db.refresh(experience)
    return experience

@router.delete("/experiences/{exp_id}")
def delete_experience(exp_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    experience = db.query(UserExperience).filter(
        UserExperience.id == exp_id,
        UserExperience.user_id == current_user.id
    ).first()
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found or not owned by you"
        )
    db.delete(experience)
    db.commit()
    return {"message": "Experience deleted successfully", "id": exp_id}
