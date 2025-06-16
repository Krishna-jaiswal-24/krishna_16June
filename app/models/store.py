from app.db.database import Base
from sqlalchemy import Column, String, DateTime, Enum, Index
import enum

class StoreStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class StoreStatus(Base):
    __tablename__ = "store_status"

    id = Column(String, primary_key=True)
    store_id = Column(String, nullable=False, index=True)
    status = Column(Enum(StoreStatusEnum), nullable=False)
    timestamp_utc = Column(DateTime(timezone=True), nullable=False, index=True)

    # Add composite index for common query patterns
    __table_args__ = (
        Index('idx_store_timestamp', 'store_id', 'timestamp_utc'),
    )        