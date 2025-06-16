from fastapi import FastAPI
from app.settings import Settings
from app.db.database import engine, Base
from app.api import report

# Initialize FastAPI app
app = FastAPI()
app.include_router(report.router)
settings = Settings()


def init_db():
    Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def on_startup():
    print(f"[INFO] Environment: {settings.ENVIRONMENT}")
    init_db()


@app.get("/")
def read_root():
    return {"message": "Health Check OK" , "status": 200}