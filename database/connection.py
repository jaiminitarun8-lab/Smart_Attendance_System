from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database file — 'attendance.db' project folder me hi ban jayegi
DATABASE_URL = "sqlite:///./attendance.db"

# connect_args zaroori hai SQLite ke liye jab FastAPI ke saath use karte hain
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI routes me ye function use hoga database session lene ke liye."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
