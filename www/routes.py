# home/routes.py
import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

www_router = APIRouter(tags=["Frontend"])

current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"current_dir", current_dir)

templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))
print(f"templates", templates.get_template("index.html"))


@www_router.get("/", response_class=HTMLResponse)
async def get_homepage(request: Request):
    script_path = "/public/script.js"
    return templates.TemplateResponse(
        "index.html", {"request": request, "script_path": script_path}
    )
