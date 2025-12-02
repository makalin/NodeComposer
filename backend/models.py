"""
Database models
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text
from sqlalchemy.sql import func
from database import Base
import uuid


class GenerationTask(Base):
    __tablename__ = "generation_tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt = Column(Text, nullable=False)
    status = Column(String, default="queued")  # queued, processing, completed, failed
    progress = Column(Float, default=0.0)
    duration = Column(Float, default=30.0)
    file_path = Column(String, nullable=True)
    model_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class ModelCheckpoint(Base):
    __tablename__ = "model_checkpoints"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=False)
    is_base = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

