# web/routes.py
from datetime import datetime, timedelta, date
from typing import Optional

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from core.config import settings
from database import SessionLocal
from models.user import User
from models.patient import Patient
from models.appointment import Appointment
from auth.jwt_handler import create_access_token, verify_access_token

router = APIRouter(tags=["Web"])
templates = Jinja2Templates(directory="templates")

COOKIE_NAME = "access_token"


def current_web_user(request: Request) -> Optional[dict]:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    return verify_access_token(token) or None


def require_web_auth(request: Request) -> Optional[dict]:
    user = current_web_user(request)
    if not user:
        raise RedirectResponse(url="/web/login", status_code=status.HTTP_303_SEE_OTHER)
    return user


@router.get("/web/login", name="web_login", response_class=HTMLResponse)
def web_login(request: Request):
    if current_web_user(request):
        return RedirectResponse(url="/web/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    ctx = {"request": request, "title": "Login", "user": None, "now": datetime.now().year, "active": "login"}
    return templates.TemplateResponse("auth/login.html", ctx)


@router.post("/web/login", name="web_login_post")
def web_login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    email = (email or "").strip().lower()

    with SessionLocal() as db:
        user: Optional[User] = db.query(User).filter(User.email == email).first()
        if not user or not settings.pwd_context.verify(password, user.password):
            ctx = {
                "request": request,
                "title": "Login",
                "error": "Credenciais inválidas",
                "user": None,
                "now": datetime.now().year,
                "active": "login",
            }
            return templates.TemplateResponse("auth/login.html", ctx, status_code=status.HTTP_401_UNAUTHORIZED)

        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(sub=user.email, extra={"uid": user.id, "role": user.role}, expires_delta=expires_delta)

    resp = RedirectResponse(url="/web/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=int(expires_delta.total_seconds()),
        secure=False,  # mude para True em produção (HTTPS)
        path="/",
    )
    return resp


@router.get("/web/logout", name="web_logout")
def web_logout():
    resp = RedirectResponse(url="/web/login", status_code=status.HTTP_303_SEE_OTHER)
    resp.delete_cookie(COOKIE_NAME, path="/")
    return resp


@router.get("/web/dashboard", name="web_dashboard", response_class=HTMLResponse)
def web_dashboard(request: Request):
    user = current_web_user(request)
    if not user:
        return RedirectResponse(url="/web/login", status_code=status.HTTP_303_SEE_OTHER)

    today = date.today()
    tomorrow = date.fromordinal(today.toordinal() + 1)

    with SessionLocal() as db:
        patients_count = db.query(Patient).count()
        appts_today = (
            db.query(Appointment)
            .filter(Appointment.date >= datetime.combine(today, datetime.min.time()))
            .filter(Appointment.date < datetime.combine(tomorrow, datetime.min.time()))
            .count()
        )

    ctx = {
        "request": request,
        "title": "Dashboard",
        "user": user,
        "now": datetime.now().year,
        "active": "dashboard",
        "kpi": {
            "patients": patients_count,
            "appts_today": appts_today,
        },
    }
    return templates.TemplateResponse("dashboard/index.html", ctx)


@router.get("/web/patients", name="web_patients", response_class=HTMLResponse)
def web_patients(request: Request):
    user = current_web_user(request)
    if not user:
        return RedirectResponse(url="/web/login", status_code=status.HTTP_303_SEE_OTHER)

    with SessionLocal() as db:
        patients = db.query(Patient).order_by(Patient.name.asc()).limit(100).all()

    ctx = {
        "request": request,
        "title": "Pacientes",
        "user": user,
        "now": datetime.now().year,
        "active": "patients",
        "patients": patients,
    }
    return templates.TemplateResponse("patients/list.html", ctx)

