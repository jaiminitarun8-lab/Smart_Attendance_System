from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database.connection import get_db
from database.models import Notification

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class NotificationCreate(BaseModel):
    user_id: str
    user_type: str   # "student" ya "faculty"
    title: str


def _serialize(n: Notification):
    return {
        "id": n.id,
        "title": n.title,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat() if n.created_at else None,
    }


@router.get("/{user_id}")
def get_notifications(user_id: str, db: Session = Depends(get_db)):
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    unread_count = sum(1 for n in notifications if not n.is_read)

    return {
        "success": True,
        "notifications": [_serialize(n) for n in notifications],
        "unread_count": unread_count,
    }


@router.post("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        return {"success": False, "message": "Notification not found."}
    notif.is_read = True
    db.commit()
    return {"success": True}


@router.post("/{user_id}/read-all")
def mark_all_read(user_id: str, db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).update(
        {"is_read": True}
    )
    db.commit()
    return {"success": True}


@router.post("")
def create_notification(data: NotificationCreate, db: Session = Depends(get_db)):
    """Internal use — dusre routes (leave, tasks, marks) yahan se notification bhej sakte hain."""
    notif = Notification(user_id=data.user_id, user_type=data.user_type, title=data.title)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return {"success": True, "id": notif.id}
