from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/faculty", tags=["faculty"])
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard")
def faculty_dashboard(request: Request):
    return templates.TemplateResponse(request=request, name="faculty_dashboard.html")
