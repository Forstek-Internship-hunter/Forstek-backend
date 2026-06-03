from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    company = Column(String(255))
    location = Column(String(255))
    description = Column(Text)
    url = Column(String(500), unique=True)
    source = Column(String(100))  # linkedin, tanitjobs, indeed
    created_at = Column(DateTime, default=func.now())

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer)
    cover_letter = Column(Text)
    status = Column(Enum("pending", "sent", "rejected", "accepted"), default="pending")
    created_at = Column(DateTime, default=func.now())

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    speciality = Column(String(255))  # ex: Cloud, DevOps, FullStack
    skills = Column(Text)             # ex: Docker, Kubernetes, Angular
    stage_type = Column(String(100))  # "pfe", "ete", "both"
    location = Column(String(255))    # ex: Tunis, Remote, Both
    languages = Column(String(100))   # "fr", "en", "both"
    created_at = Column(DateTime, default=func.now())