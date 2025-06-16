import pandas as pd
from sqlalchemy.orm import Session
from app.models.store import StoreStatus, StoreStatusEnum
from app.models.timezone import StoreTimezone
from app.models.hours import BusinessHour
from datetime import datetime
from app.db.database import get_db
import os


def parse_timestamp(timestamp_str: str) -> datetime:
    return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f %Z")


def load_and_insert_csv_data(db: Session):
    # 1. Load store_status.csv
    df_status = pd.read_csv("../data/store_status.csv")
    status_data = [
        StoreStatus(
            store_id=row["store_id"],
            status=StoreStatusEnum(row["status"]),
            timestamp_utc=parse_timestamp(row["timestamp_utc"])
        )
        for _, row in df_status.iterrows()
    ]
    db.bulk_save_objects(status_data)
    db.commit()

    # 2. Load menu_hours.csv
    df_menu = pd.read_csv("../data/menu_hours.csv")
    menu_data = [
        BusinessHour(
            store_id=row["store_id"],
            dayOfWeek=row["dayOfWeek"],
            start_time_local=row["start_time_local"],
            end_time_local=row["end_time_local"]
        )
        for _, row in df_menu.iterrows()
    ]
    db.bulk_save_objects(menu_data)
    db.commit()

    # 3. Load timezones.csv
    df_tz = pd.read_csv("../data/timezones.csv")
    tz_data = [
        StoreTimezone(
            store_id=row["store_id"],
            timezone_str=row["timezone_str"]
        )
        for _, row in df_tz.iterrows()
    ]
    db.bulk_save_objects(tz_data)
    db.commit()

    print("[INFO] ✅ All CSV files successfully inserted into the database.")


def get_report_file(report_id: str = "b7bda8fc-7dde-4c96-aba4-276c75989e43") -> str:
    """
    Returns the path to the specified report file.
    
    Args:
        report_id (str): The ID of the report file to return
        
    Returns:
        str: The absolute path to the report file
    """
    # Get the absolute path to the project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    # Construct the path to the report file
    report_path = os.path.join(project_root, "reports", f"{report_id}.csv")
    
    if not os.path.exists(report_path):
        raise FileNotFoundError(f"Report file not found: {report_path}")
        
    return report_path


if __name__ == "__main__":
    db = next(get_db())
    load_and_insert_csv_data(db)