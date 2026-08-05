from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from routes import auth, student, faculty, face, tasks, marks, activities

# Chatbot temporarily disabled
# from routes import chatbot

app = FastAPI(title="Smart Attendance System")

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Routers
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(faculty.router)
app.include_router(face.router)
app.include_router(tasks.router)
app.include_router(marks.router)
app.include_router(activities.router)

# Chatbot temporarily disabled
# app.include_router(chatbot.router)


@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )