from fastapi import APIRouter
from pydantic import BaseModel

from ai.attendance import get_attendance
from ai.leave import get_leave
from ai.today import get_today_attendance
from ai.subject import get_subject_attendance
from ai.intent import detect_intent
from ai.predictor import predict_attendance

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    user_id: str
    role: str


@router.post("/api/chat")
def chat(data: ChatRequest):

    msg = data.message.lower()
    intent = detect_intent(msg)

    # ==========================
    # Attendance
    # ==========================
    if intent == "attendance":

        result = get_attendance(data.user_id)

        return {
            "reply": f"""📊 Attendance Report

Present : {result['present']}
Total Classes : {result['total']}
Attendance : {result['percentage']}%
"""
        }

    # ==========================
    # Leave
    # ==========================
    elif intent == "leave":

        leave = get_leave(data.user_id)

        return {
            "reply": f"""📄 Leave Status

Status : {leave['status']}
Reason : {leave['reason']}
"""
        }

    # ==========================
    # Today's Attendance
    # ==========================
    elif intent == "today":

        today = get_today_attendance(data.user_id)

        if today:
            return {
                "reply": f"""📅 Today's Attendance

Subject : {today['subject']}

Status : {today['status']}

Date : {today['date']}
"""
            }

        return {
            "reply": "No attendance found."
        }

    # ==========================
    # Mathematics Attendance
    # ==========================
    elif intent == "mathematics":

        result = get_subject_attendance(
            data.user_id,
            "Mathematics"
        )

        if result:
            return {
                "reply": f"""📚 Mathematics Attendance

Present : {result['present']}
Total : {result['total']}
Attendance : {result['percentage']}%
"""
            }

        return {
            "reply": "No Mathematics attendance found."
        }

    # ==========================
    # Attendance Prediction
    # ==========================
    elif intent == "prediction":

        result = predict_attendance(data.user_id)

        if result:
            return {
                "reply": f"""📈 Attendance Prediction

Current Attendance : {result['current']}%

Target : {result['target']}%

Need {result['needed']} more continuous present classes to reach {result['target']}%.
"""
            }

        return {
            "reply": "Attendance data not found."
        }

    # ==========================
    # Greeting
    # ==========================
    elif "hello" in msg or "hi" in msg:

        return {
            "reply": "Hello 👋 Welcome to Smart Attendance AI Assistant."
        }

    # ==========================
    # Gemini AI
    # ==========================
    else:

        try:

            reply = ask_gemini(data.message)

            return {
                "reply": reply
            }

        except Exception as e:

            return {
                "reply": f"Gemini Error: {str(e)}"
            }