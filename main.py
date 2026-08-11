from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from routes import (auth, student, faculty, face,tasks, marks, activities,leave, register, notifications,attendance,timetable, chatbot)


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