from fastapi import APIRouter
from pydantic import BaseModel

from ai.attendance import get_attendance
from ai.leave import get_leave
from ai.today import get_today_attendance
from ai.subject import get_subject_attendance
from ai.intent import detect_intent
from ai.predictor import predict_attendance


router = APIRouter()


# =====================================================
# Chat Request Model
# =====================================================

class ChatRequest(BaseModel):
    message: str
    user_id: str = ""
    role: str = "student"


# =====================================================
# Chat API
# =====================================================

@router.post("/api/chat")
def chat(data: ChatRequest):

    try:

        # User message
        msg = data.message.lower().strip()

        # Detect intent
        intent = detect_intent(msg)


        # =================================================
        # Greeting
        # =================================================

        if (
            "hello" in msg
            or "hi" in msg
            or "hey" in msg
            or "hii" in msg
            or "helo" in msg
        ):

            return {
                "reply": (
                    "Hello 👋\n\n"
                    "Welcome to Smart Attendance AI Assistant.\n\n"
                    "I can help you with:\n"
                    "• Attendance\n"
                    "• Leave status\n"
                    "• Today's attendance\n"
                    "• Mathematics attendance\n"
                    "• Attendance prediction"
                )
            }


        # =================================================
        # Check User ID
        # =================================================

        if not data.user_id:

            return {
                "reply": (
                    "⚠️ Student ID not found.\n\n"
                    "Please login again and then use the chatbot."
                )
            }


        # =================================================
        # Attendance
        # =================================================

        if intent == "attendance":

            result = get_attendance(data.user_id)

            if result:

                return {
                    "reply": (
                        "📊 Attendance Report\n\n"
                        f"Present : {result.get('present', 0)}\n"
                        f"Total Classes : {result.get('total', 0)}\n"
                        f"Attendance : {result.get('percentage', 0)}%"
                    )
                }

            return {
                "reply": "No attendance data found."
            }


        # =================================================
        # Leave
        # =================================================

        elif intent == "leave":

            leave = get_leave(data.user_id)

            if leave:

                return {
                    "reply": (
                        "📄 Leave Status\n\n"
                        f"Status : {leave.get('status', 'Not available')}\n"
                        f"Reason : {leave.get('reason', 'Not available')}"
                    )
                }

            return {
                "reply": "No leave record found."
            }


        # =================================================
        # Today's Attendance
        # =================================================

        elif intent == "today":

            today = get_today_attendance(data.user_id)

            if today:

                return {
                    "reply": (
                        "📅 Today's Attendance\n\n"
                        f"Subject : {today.get('subject', 'N/A')}\n"
                        f"Status : {today.get('status', 'N/A')}\n"
                        f"Date : {today.get('date', 'N/A')}"
                    )
                }

            return {
                "reply": "No attendance found for today."
            }


        # =================================================
        # Mathematics Attendance
        # =================================================

        elif intent == "mathematics":

            result = get_subject_attendance(
                data.user_id,
                "Mathematics"
            )

            if result:

                return {
                    "reply": (
                        "📚 Mathematics Attendance\n\n"
                        f"Present : {result.get('present', 0)}\n"
                        f"Total : {result.get('total', 0)}\n"
                        f"Attendance : {result.get('percentage', 0)}%"
                    )
                }

            return {
                "reply": "No Mathematics attendance found."
            }


        # =================================================
        # Attendance Prediction
        # =================================================

        elif intent == "prediction":

            result = predict_attendance(data.user_id)

            if result:

                return {
                    "reply": (
                        "📈 Attendance Prediction\n\n"
                        f"Current Attendance : {result.get('current', 0)}%\n"
                        f"Target : {result.get('target', 75)}%\n"
                        f"Need {result.get('needed', 0)} more continuous "
                        f"present classes to reach "
                        f"{result.get('target', 75)}%."
                    )
                }

            return {
                "reply": "Attendance data not found."
            }


        # =================================================
        # Default Response
        # =================================================

        else:

            return {
                "reply": (
                    "🤖 I am AttendAI Assistant.\n\n"
                    "Try asking:\n\n"
                    "📊 What is my attendance?\n"
                    "📄 Show my leave status\n"
                    "📅 What is today's attendance?\n"
                    "📚 Show Mathematics attendance\n"
                    "📈 Predict my attendance"
                )
            }


    # =====================================================
    # Error Handling
    # =====================================================

    except Exception as e:

        print("CHATBOT ERROR:", str(e))

        return {
            "reply": (
                "❌ Sorry, something went wrong while "
                "processing your request."
            )
        }