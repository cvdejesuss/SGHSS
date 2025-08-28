# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from time import monotonic

from core.config import settings, AppInfo
from routers import patient_router, auth_router, appointment_router, record_router
from routers import item_router, stock_router

description = """
SGHSS — Sistema de Gestão Hospitalar e de Saúde.

Este backend oferece módulos de **Pacientes**, **Autenticação**, **Consultas**, **Prontuário**, **Estoque** e **Itens**.
"""

app = FastAPI(
    title=settings.APP_NAME,
    description=description,
    version="0.1.0",
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Middleware simples de latência e request-id (header opcional)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = monotonic()
    response = await call_next(request)
    process_time = monotonic() - start
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    # Propaga um request id se vier do front (útil pra logs correlacionados)
    req_id = request.headers.get("X-Request-ID")
    if req_id:
        response.headers["X-Request-ID"] = req_id
    return response

# Handlers básicos de erro (mensagens mais consistentes)
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno inesperado. Tente novamente mais tarde."},
    )

# Inclui routers com prefixo de versão
api_prefix = settings.API_V1_PREFIX
app.include_router(patient_router.router, prefix=api_prefix, tags=["Pacientes"])
app.include_router(auth_router.router, prefix=api_prefix, tags=["Auth"])
app.include_router(appointment_router.router, prefix=api_prefix, tags=["Consultas"])
app.include_router(record_router.router, prefix=api_prefix, tags=["Prontuários"])
app.include_router(item_router.router, prefix=api_prefix, tags=["Itens"])
app.include_router(stock_router.router, prefix=api_prefix, tags=["Estoque"])

@app.get("/")
def read_root():
    """
    Endpoint de boas-vindas (não versionado) — útil para checar se o serviço está de pé.
    """
    return {"msg": f"{settings.APP_NAME} está rodando"}

@app.get(f"{api_prefix}/healthz")
def healthz():
    """
    Liveness probe — indica se a aplicação está viva.
    """
    return {"status": "ok"}

@app.get(f"{api_prefix}/readiness")
def readiness():
    """
    Readiness probe — aqui podemos, no futuro, testar conexão com DB/mensageria.
    """
    return {"status": "ready"}

@app.get(f"{api_prefix}/info", response_model=AppInfo)
def info():
    """
    Informações úteis para o front/monitoramento.
    """
    return AppInfo(
        name=settings.APP_NAME,
        env=settings.APP_ENV,
        version="0.1.0",
        docs="/docs",
    )

