from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from routes import auth, student, faculty, chatbot
app = FastAPI(title="Smart Attendance System")

# Static files (CSS, JS, images) — accessible via /static/...
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML templates folder
templates = Jinja2Templates(directory="templates")

# Backend routes
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(faculty.router)
app.include_router(chatbot.router)


@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )
