# main.py

from time import monotonic
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from core.config import settings, AppInfo

# importe APENAS os routers; não inclua nada fora deste arquivo
from routers import (
    auth_router,
    patient_router,
    appointment_router,
    record_router,
    item_router,
    stock_router,
    user_admin_router,
)

description = """
SGHSS — Sistema de Gestão Hospitalar e de Saúde.
Módulos: Auth, Pacientes, Consultas, Prontuários, Itens e Estoque.
"""

app = FastAPI(
    title=settings.APP_NAME,
    description=description,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS (ajuste conforme seu front)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Static (para servir Skote/HTML, imagens, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Middleware simples de latência e request-id
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = monotonic()
    response = await call_next(request)
    process_time = monotonic() - start
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    req_id = request.headers.get("X-Request-ID")
    if req_id:
        response.headers["X-Request-ID"] = req_id
    return response

# === Inclua cada router UMA única vez, com o mesmo prefixo global ===
api_prefix = settings.API_V1_PREFIX

app.include_router(auth_router.router,        prefix=api_prefix)  # /api/v1/auth/...
app.include_router(patient_router.router,     prefix=api_prefix)  # /api/v1/patients/...
app.include_router(appointment_router.router, prefix=api_prefix)  # /api/v1/appointments/...
app.include_router(record_router.router,      prefix=api_prefix)  # /api/v1/patients/{id}/records/...
app.include_router(item_router.router,        prefix=api_prefix)  # /api/v1/items/...
app.include_router(stock_router.router,       prefix=api_prefix)  # /api/v1/stock/...
app.include_router(user_admin_router.router,  prefix=api_prefix)  # /api/v1/users/...

# Rotas Web (páginas HTML com Jinja2) — opcional, se existir web/routes.py
try:
    from web.routes import router as web_router
    app.include_router(web_router)
except Exception:
    pass

# Painel Admin (SQLAdmin) — opcional, se existir admin_panel.py
try:
    from admin_panel import mount_admin
    mount_admin(app)
except Exception:
    pass

# Endpoints utilitários
@app.get("/")
def read_root():
    return {"msg": f"{settings.APP_NAME} está rodando"}

@app.get(f"{api_prefix}/healthz")
def healthz():
    return {"status": "ok"}

@app.get(f"{api_prefix}/readiness")
def readiness():
    return {"status": "ready"}

@app.get(f"{api_prefix}/info", response_model=AppInfo)
def info():
    return AppInfo()



