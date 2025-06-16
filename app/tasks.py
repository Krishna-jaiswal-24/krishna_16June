from app.celery_app import celery_app
from app.services.report_generator import generate_report
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.report import Report

@celery_app.task(name="generate_store_report")
def generate_store_report(report_id: str):
    """Celery task to generate store report"""
    db: Session = next(get_db())
    try:
        # Update status to Running
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            return {"error": "Report not found"}
            
        report.status = "Running"
        db.commit()
        
        # Generate report
        report_data = generate_report(report_id)
        
        # Update report status and data
        report.status = "Complete"
        report.result = report_data
        db.commit()
        
        return report_data
        
    except Exception as e:
        # Update report status to Failed
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            report.status = "Failed"
            report.error = str(e)
            db.commit()
        return {"error": str(e)} 