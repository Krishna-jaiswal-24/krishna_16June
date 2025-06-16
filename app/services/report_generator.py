# app/services/report_generator.py

import pandas as pd
from datetime import datetime, timedelta, time
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.store import StoreStatus, StoreStatusEnum
from app.models.timezone import StoreTimezone
from app.models.hours import BusinessHour
import pytz
import os
from typing import List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


def get_store_timezone(db: Session, store_id: str) -> str:
    """Get store's timezone or default to America/Chicago."""
    timezone = db.query(StoreTimezone).filter(StoreTimezone.store_id == store_id).first()
    return timezone.timezone_str if timezone else "America/Chicago"


def get_business_hours(db: Session, store_id: str) -> list:
    """Get store's business hours."""
    return db.query(BusinessHour).filter(BusinessHour.store_id == store_id).all()


def parse_time(time_str: str) -> time:
    """Parse time string to time object."""
    try:
        return datetime.strptime(time_str, "%H:%M:%S").time()
    except ValueError:
        logger.warning(f"Invalid time format: {time_str}")
        return time(0, 0, 0)


def is_within_business_hours(timestamp: datetime, business_hours: list) -> bool:
    """Check if timestamp is within business hours."""
    if not business_hours:
        return True  # If no business hours defined, consider store always open
    
    weekday = timestamp.weekday()
    for hours in business_hours:
        if hours.dayOfWeek == weekday:
            start_time = parse_time(hours.start_time_local)
            end_time = parse_time(hours.end_time_local)
            current_time = timestamp.time()
            
            if start_time <= current_time <= end_time:
                return True
    return False


def calculate_uptime_downtime(db: Session, store_id: str, start_time: datetime, end_time: datetime) -> Tuple[float, float]:
    """Calculate uptime and downtime for a store within a time period."""
    try:
        # Get store's timezone
        timezone_record = db.query(StoreTimezone).filter(StoreTimezone.store_id == store_id).first()
        timezone = timezone_record.timezone_str if timezone_record else "UTC"
        
        # Get business hours
        business_hours = db.query(BusinessHour).filter(BusinessHour.store_id == store_id).all()
        
        # Get all status observations for the store in the time period
        status_observations = db.query(StoreStatus).\
            filter(
                StoreStatus.store_id == store_id,
                StoreStatus.timestamp_utc >= start_time,
                StoreStatus.timestamp_utc <= end_time
            ).\
            order_by(StoreStatus.timestamp_utc).\
            all()
        
        if not status_observations:
            logger.debug(f"No status observations found for store {store_id} between {start_time} and {end_time}")
            return 0.0, 0.0
        
        total_uptime = 0
        total_downtime = 0
        
        # Pre-calculate timezone conversion
        tz = pytz.timezone(timezone)
        
        # Calculate time differences between consecutive observations
        for i in range(len(status_observations) - 1):
            current = status_observations[i]
            next_obs = status_observations[i + 1]
            
            # Convert timestamps to store's local timezone
            current_time = current.timestamp_utc.astimezone(tz)
            next_time = next_obs.timestamp_utc.astimezone(tz)
            
            # Calculate time difference in seconds
            time_diff = (next_time - current_time).total_seconds()
            
            # Check if the time period is within business hours
            if is_within_business_hours(current_time, business_hours):
                if current.status == StoreStatusEnum.active:
                    total_uptime += time_diff
                elif current.status == StoreStatusEnum.inactive:
                    total_downtime += time_diff
                else:
                    logger.warning(f"Unknown status value: {current.status} for store {store_id}")
        
        # Handle the last observation
        last_obs = status_observations[-1]
        last_time = last_obs.timestamp_utc.astimezone(tz)
        end_time_local = end_time.astimezone(tz)
        
        if last_time < end_time_local:
            final_diff = (end_time_local - last_time).total_seconds()
            if is_within_business_hours(last_time, business_hours):
                if last_obs.status == StoreStatusEnum.active:
                    total_uptime += final_diff
                elif last_obs.status == StoreStatusEnum.inactive:
                    total_downtime += final_diff
        
        # Convert seconds to hours
        return total_uptime / 3600, total_downtime / 3600
        
    except Exception as e:
        logger.error(f"Error calculating uptime/downtime for store {store_id}: {str(e)}")
        db.rollback()
        return 0.0, 0.0


def generate_report(db: Session) -> dict:
    """Generate a report for all stores."""
    try:
        # Get all unique store IDs with a single optimized query
        store_ids = [str(store[0]) for store in db.query(StoreStatus.store_id).distinct().all()]
        
        if not store_ids:
            logger.warning("No stores found in the database")
            return None
        
        # Get the latest timestamp with an optimized query
        latest_timestamp = db.query(StoreStatus.timestamp_utc).\
            order_by(StoreStatus.timestamp_utc.desc()).\
            first()[0]
        
        one_hour_ago = latest_timestamp - timedelta(hours=1)
        one_day_ago = latest_timestamp - timedelta(days=1)
        one_week_ago = latest_timestamp - timedelta(weeks=1)
        
        # Process stores in batches
        BATCH_SIZE = 50
        report_data = []
        total_stores = len(store_ids)
        
        logger.info(f"Starting report generation for {total_stores} stores...")
        
        for batch_start in range(0, total_stores, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, total_stores)
            batch_stores = store_ids[batch_start:batch_end]
            
            logger.info(f"Processing batch {batch_start//BATCH_SIZE + 1}/{(total_stores + BATCH_SIZE - 1)//BATCH_SIZE}")
            
            for store_id in batch_stores:
                try:
                    # Calculate uptime/downtime for different time periods
                    last_hour = calculate_uptime_downtime(db, store_id, one_hour_ago, latest_timestamp)
                    last_day = calculate_uptime_downtime(db, store_id, one_day_ago, latest_timestamp)
                    last_week = calculate_uptime_downtime(db, store_id, one_week_ago, latest_timestamp)
                    
                    store_report = {
                        "store_id": store_id,
                        "uptime_last_hour": round(last_hour[0], 2),
                        "uptime_last_day": round(last_day[0], 2),
                        "uptime_last_week": round(last_week[0], 2),
                        "downtime_last_hour": round(last_hour[1], 2),
                        "downtime_last_day": round(last_day[1], 2),
                        "downtime_last_week": round(last_week[1], 2)
                    }
                    report_data.append(store_report)
                    
                except Exception as e:
                    logger.error(f"Error processing store {store_id}: {str(e)}")
                    continue
        
        if not report_data:
            logger.warning("No valid report data generated")
            return None
        
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"store_report_{timestamp}.csv"
        filepath = os.path.join(reports_dir, filename)
        
        # Convert to DataFrame and save as CSV efficiently
        df = pd.DataFrame(report_data)
        df.to_csv(filepath, index=False)
        
        logger.info(f"Report saved to {filepath}")
        logger.info(f"Successfully processed {len(report_data)} out of {total_stores} stores")
        
        return {
            "report_data": report_data,
            "filename": filename,
            "filepath": filepath,
            "total_stores_processed": len(report_data),
            "total_stores": total_stores
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        db.rollback()
        return None