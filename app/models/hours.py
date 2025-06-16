# model for business hours

from sqlalchemy import Column, String, Integer
from app.db.database import Base

class BusinessHour(Base):
    __tablename__ = "business_hours"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Unique identifier for the business hour entry
    store_id = Column(String, nullable=False)  # Unique identifier for the store
    dayOfWeek = Column(Integer, nullable=False)  # 0 = Monday, 6 = Sunday
    start_time_local = Column(String, nullable=False)  # HH:MM:SS
    end_time_local = Column(String, nullable=False)  # HH:MM:SS       