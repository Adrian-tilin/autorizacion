"""
Sistema de Autenticación Simple
Miniproyecto educativo para aprender autenticación web
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

# Importar el router y la función get_current_user desde mis_rutas
from mis_rutas import router, get_current_user

# ==================== CONFIGURACIÓN ====================

app = FastAPI(title="Sistema de Autenticación Simple")

SECRET_KEY = "mi-clave-secreta-super-segura-123"
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

templates = Jinja2Templates(directory="templates")

# ==================== INCLUIR RUTAS ====================

# Incluir todas las rutas desde mis_rutas.py
app.include_router(router)

# ==================== MANEJO DE ERRORES ====================


@app.exception_handler(401)
async def unauthorized_handler(request: Request, exc: HTTPException):
    """Redirige al login si no está autenticado"""
    return RedirectResponse(url="/login", status_code=303)


@app.exception_handler(403)
async def forbidden_handler(request: Request, exc: HTTPException):
    """Muestra error de acceso denegado"""
    user = get_current_user(request)
    return templates.TemplateResponse(
        "error_403.html",
        {"request": request, "user": user, "message": exc.detail},
        status_code=403,
    )

app = app 