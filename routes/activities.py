from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Activity

router = APIRouter(prefix="/api/activities", tags=["activities"])


@router.get("")
def get_activities(db: Session = Depends(get_db)):
    announcements = db.query(Activity).filter(Activity.type == "announcement").order_by(Activity.created_at.desc()).all()
    extracurricular = db.query(Activity).filter(Activity.type == "extracurricular").order_by(Activity.created_at.desc()).all()

    def serialize(a):
        return {
            "title": a.title,
            "description": a.description,
            "event_date": a.event_date.isoformat() if a.event_date else None,
        }

    return {
        "success": True,
        "announcements": [serialize(a) for a in announcements],
        "extracurricular": [serialize(a) for a in extracurricular],
    }
