from app.celery_app import celery_app
from app.services.report_generator import generate_report
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.report import Report
import logging
from sqlalchemy.exc import SQLAlchemyError
import json
from uuid import UUID

logger = logging.getLogger(__name__)

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

def update_report_status(report_id: str, status: str, error: str = None, result: dict = None):
    """Update report status in a new database session."""
    db = next(get_db())
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        if report:
            report.status = status
            if error is not None:
                report.error = error
            if result is not None:
                # Convert UUIDs to strings in the result
                report.result = json.loads(json.dumps(result, cls=UUIDEncoder))
            db.commit()
            logger.info(f"Updated report {report_id} status to {status}")
            if result and "total_stores_processed" in result:
                logger.info(f"Processed {result['total_stores_processed']} out of {result['total_stores']} stores")
                if "filepath" in result:
                    logger.info(f"Report saved to: {result['filepath']}")
        else:
            logger.error(f"Report {report_id} not found")
    except Exception as e:
        logger.error(f"Error updating report status: {str(e)}")
        db.rollback()
    finally:
        db.close()

@celery_app.task(name='generate_store_report')
def generate_store_report(report_id: str):
    """Generate a report for all stores."""
    # Update initial status
    update_report_status(report_id, "Running")
    
    try:
        # Get a new session for report generation
        db = next(get_db())
        try:
            # Generate the report
            report_data = generate_report(db)
            
            if not report_data:
                error_msg = "No report data generated"
                logger.error(error_msg)
                update_report_status(report_id, "Failed", error=error_msg)
                return None
            
            # Update report with results using a new session
            update_report_status(report_id, "Complete", result=report_data)
            
            logger.info(f"Successfully generated report {report_id}")
            return report_data
            
        except SQLAlchemyError as e:
            error_msg = f"Database error generating report: {str(e)}"
            logger.error(error_msg)
            db.rollback()
            update_report_status(report_id, "Failed", error=error_msg)
            raise
        except Exception as e:
            error_msg = f"Error generating report: {str(e)}"
            logger.error(error_msg)
            db.rollback()
            update_report_status(report_id, "Failed", error=error_msg)
            raise
        finally:
            db.close()
            
    except Exception as e:
        error_msg = f"Unexpected error in report generation task: {str(e)}"
        logger.error(error_msg)
        update_report_status(report_id, "Failed", error=error_msg)
        raise 