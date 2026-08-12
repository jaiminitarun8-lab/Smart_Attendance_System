from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from routes import (activities, attendance, auth, chatbot, face, faculty,
                    leave, marks, notifications, profile, register, student,
                    tasks, timetable)

# =====================================================
# FastAPI Application
# =====================================================

app = FastAPI(
    title="Smart Attendance System"
)


# =====================================================
# Static Files
# =====================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =====================================================
# HTML Templates
# =====================================================

templates = Jinja2Templates(
    directory="templates"
)


# =====================================================
# Backend Routers
# =====================================================

app.include_router(auth.router)

app.include_router(student.router)

app.include_router(faculty.router)

app.include_router(face.router)

app.include_router(tasks.router)

app.include_router(marks.router)

app.include_router(activities.router)

app.include_router(leave.router)

app.include_router(register.router)

app.include_router(notifications.router)

app.include_router(attendance.router)

app.include_router(timetable.router)
app.include_router(profile.router)


# =====================================================
# 🤖 Chatbot Router
# =====================================================

app.include_router(chatbot.router)


# =====================================================
# Login Page
# =====================================================

@app.get("/")
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


# =====================================================
# Register Page
# =====================================================

@app.get("/register")
def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )
# =====================================================
# Privacy Policy Page
# =====================================================

@app.get("/privacy")
def privacy_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="privacy.html"
    )
# =====================================================
# Terms & Conditions Page
# =====================================================

@app.get("/terms")
def terms_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="terms.html"
    )
