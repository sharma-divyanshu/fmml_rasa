from sqlalchemy import create_engine, Column, String, Boolean, Integer, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
import os
from typing import Optional, List, Dict, Any

from ..config.settings import config

# Create SQLAlchemy engine and session
engine = create_engine(config.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User preferences
    default_voice_id = Column(String, default=config.voice_id)
    
    # Relationships
    logs = relationship("PeriodLog", back_populates="user")

class PeriodLog(Base):
    __tablename__ = "period_logs"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Period data
    flow = Column(String)  # light, medium, heavy
    spotting = Column(Boolean, default=False)
    
    # Symptoms and mood
    mood = Column(JSON, default=list)  # List of mood strings
    symptoms = Column(JSON, default=list)  # List of symptom strings
    notes = Column(String, nullable=True)
    
    # Voice data
    voice_note_path = Column(String, nullable=True)
    transcribed_text = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="logs")

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Create a default user if none exists
    db = SessionLocal()
    try:
        if not db.query(User).first():
            default_user = User(id="default_user")
            db.add(default_user)
            db.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

# Initialize the database when this module is imported
init_db()
