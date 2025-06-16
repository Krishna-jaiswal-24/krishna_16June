from sqlalchemy import Column, String
from app.db.database import Base

class StoreTimezone(Base):
    __tablename__ = "store_timezone"

    store_id = Column(String, primary_key=True)
    timezone_str = Column(String, nullable=False)