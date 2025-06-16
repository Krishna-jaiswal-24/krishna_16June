# app/api/report.py

from fastapi import APIRouter, HTTPException
from uuid import uuid4
from app.tasks.report_tasks import generate_store_report
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.report import Report
import pandas as pd
import os

router = APIRouter()


@router.get("/trigger_report")
def trigger_report():
    """Trigger a new report generation"""
    db: Session = next(get_db())
    
    # Create new report record
    report_id = str(uuid4())
    report = Report(
        id=report_id,
        status="Pending"
    )
    db.add(report)
    db.commit()
    
    # Trigger Celery task
    generate_store_report.delay(report_id)
    
    return {"report_id": report_id}


@router.get("/get_report/{report_id}")
def get_report(report_id: str):
    """Get report status and data"""
    db: Session = next(get_db())
    
    # Get report from database
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.status == "Running":
        return {"status": "Running"}
    elif report.status == "Failed":
        return {"status": "Failed", "error": report.error}
    elif report.status == "Complete":
        if not report.result:
            raise HTTPException(status_code=404, detail="Report data not found")
        return {
            "status": "Complete",
            "data": report.result
        }
    else:
        return {"status": report.status}