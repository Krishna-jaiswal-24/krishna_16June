# Store Status Monitoring System

A FastAPI-based system for monitoring store status and generating reports on store uptime and downtime.

## Features

- Real-time store status monitoring
- Business hours tracking
- Timezone-aware calculations
- Automated report generation
- CSV export functionality
- Asynchronous task processing with Celery
- PostgreSQL database with SQLAlchemy ORM

## Architecture

The system consists of several key components:

### 1. API Layer
- FastAPI application handling HTTP requests
- Endpoints for triggering reports and retrieving report status
- RESTful API design

### 2. Data Models
- `StoreStatus`: Tracks store status changes
- `StoreTimezone`: Stores timezone information
- `BusinessHour`: Defines store operating hours
- `Report`: Manages report generation and status

### 3. Services
- Report generation service
- Status calculation service
- CSV export service

### 4. Task Processing
- Celery for asynchronous task processing
- Redis as message broker and result backend
- Background report generation

## Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis
- Docker (optional)

### Environment Variables
Create a `.env` file with the following variables:
```env
ENVIRONMENT=development
DATABASE_URL=postgresql://user:password@localhost:5432/store_monitor
JWT_SECRET=your_jwt_secret
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd store-monitor
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python -m app.init_db
```

5. Download and prepare data files:
```bash
# Create data directory
mkdir -p data

# Download data files (you'll need to provide these files separately)
# Place the following files in the data directory:
# - store_status.csv
# - store_timezone.csv
# - business_hours.csv
```

6. Load initial data:
```bash
python -m app.utils.csv_loader
```

### Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

2. Start Celery worker:
```bash
celery -A app.celery_app worker --loglevel=info
```

3. Start Redis (if not running):
```bash
redis-server
```

## API Endpoints

### 1. Trigger Report Generation
```http
GET /trigger_report
```
Response:
```json
{
    "report_id": "uuid-string"
}
```

### 2. Get Report Status
```http
GET /get_report/{report_id}
```
Response:
```json
{
    "status": "Complete",
    "data": {
        "report_data": [...],
        "filename": "store_report_YYYYMMDD_HHMMSS.csv",
        "filepath": "/path/to/report.csv",
        "total_stores_processed": 100,
        "total_stores": 100
    }
}
```

## Report Generation

The system generates reports with the following metrics:
- Uptime in the last hour
- Uptime in the last day
- Uptime in the last week
- Downtime in the last hour
- Downtime in the last day
- Downtime in the last week

Reports are saved as CSV files in the `app/reports` directory.

## Data Models

### StoreStatus
- `id`: String (Primary Key)
- `store_id`: String
- `status`: Enum (active/inactive)
- `timestamp_utc`: DateTime

### StoreTimezone
- `store_id`: String (Primary Key)
- `timezone_str`: String

### BusinessHour
- `id`: Integer (Primary Key)
- `store_id`: String
- `dayOfWeek`: Integer (0-6)
- `start_time_local`: String
- `end_time_local`: String

### Report
- `id`: String (Primary Key)
- `status`: String
- `error`: String (Optional)
- `created_at`: DateTime
- `updated_at`: DateTime
- `result`: JSON

## Error Handling

The system includes comprehensive error handling:
- Database transaction management
- Exception logging
- Status tracking for failed operations
- Graceful degradation

## Performance Optimizations

1. Database Optimizations:
   - Indexed columns for frequent queries
   - Composite indexes for common query patterns
   - Efficient query design

2. Report Generation:
   - Batch processing of stores
   - Asynchronous task processing
   - Memory-efficient data handling

3. Caching:
   - Redis for task queue and results
   - Efficient data structures

## Data Files

The project uses several large CSV files that are not included in the repository due to their size:

1. `data/store_status.csv` (134.16 MB)
   - Contains store status observations
   - Format: store_id, status, timestamp_utc

2. `data/store_timezone.csv`
   - Contains store timezone information
   - Format: store_id, timezone_str

3. `data/business_hours.csv`
   - Contains store business hours
   - Format: store_id, dayOfWeek, start_time_local, end_time_local

To use the application:
1. Create a `data` directory in the project root
2. Obtain the required CSV files
3. Place them in the `data` directory
4. Run the CSV loader utility to import the data

Note: These files are excluded from version control using `.gitignore` to prevent repository size issues.

## Submission Done By 
   ### Krishna Jaiswal
   ### Email: krishnajaiswal2119@gmail.com
   ### Phone: +91 8840413100


