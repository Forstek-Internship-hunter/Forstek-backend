from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    title = Column(String(255))
    company = Column(String(255))
    location = Column(String(255))
    description = Column(Text)
    url = Column(String(500))
    source = Column(String(100))  # linkedin, tanitjobs, indeed
    created_at = Column(DateTime, default=func.now())

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    offer_id = Column(Integer)
    cover_letter = Column(Text)
    status = Column(Enum("pending", "sent", "rejected", "accepted"), default="pending")
    created_at = Column(DateTime, default=func.now())


class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    name = Column(String(255))
    speciality = Column(String(255))
    skills = Column(Text)
    stage_type = Column(String(100))
    location = Column(String(255))
    languages = Column(String(100))
    created_at = Column(DateTime, default=func.now())

class UserExperience(Base):
    __tablename__ = "user_experiences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum("academic", "professional", "project", "certification"), nullable=False)
    title = Column(String(255))
    institution = Column(String(255))
    description = Column(Text)
    start_date = Column(String(50))
    end_date = Column(String(50))
    created_at = Column(DateTime, default=func.now())