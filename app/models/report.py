from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from app.db.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(String, primary_key=True)
    status = Column(String, nullable=False, default="Pending")
    error = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    result = Column(JSON, nullable=True)  # Store report data or error details 