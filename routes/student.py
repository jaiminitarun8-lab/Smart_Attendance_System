from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/student", tags=["student"])
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard")
def student_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="student_dashboard.html")
