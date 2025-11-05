"""
Rutas del sistema de autenticación
"""

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# ==================== CONFIGURACIÓN ====================

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ==================== BASE DE DATOS ====================

USERS_DB = {
    "user": {"password": "1234", "role": "user", "name": "Usuario Normal"},
    "admon": {"password": "admin", "role": "admin", "name": "Administrador"},
}

# ==================== DEPENDENCIAS ====================


def get_current_user(request: Request) -> dict | None:
    """Obtiene el usuario actual de la sesión"""
    return request.session.get("user")


def get_current_user_required(request: Request) -> dict:
    """Requiere que el usuario esté autenticado"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")
    return user


def require_admin(user: dict = Depends(get_current_user_required)) -> dict:
    """Requiere que el usuario sea administrador"""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403, detail="Acceso denegado: se requiere rol de administrador"
        )
    return user


# ==================== RUTAS PÚBLICAS ====================


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página de inicio - Pública"""
    user = get_current_user(request)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Formulario de login"""
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Procesar login"""
    # Buscar usuario en la base de datos
    user_data = USERS_DB.get(username)

    # Verificar credenciales
    if not user_data or user_data["password"] != password:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Usuario o contraseña incorrectos"},
            status_code=401,
        )

    # Crear sesión
    request.session["user"] = {
        "username": username,
        "name": user_data["name"],
        "role": user_data["role"],
    }

    # Redirigir según el rol
    if user_data["role"] == "admin":
        return RedirectResponse(url="/admon", status_code=303)
    else:
        return RedirectResponse(url="/informe", status_code=303)


@router.get("/logout")
async def logout(request: Request):
    """Cerrar sesión"""
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


# ==================== RUTAS PROTEGIDAS ====================


@router.get("/informe", response_class=HTMLResponse)
async def informe(request: Request, user: dict = Depends(get_current_user_required)):
    """Página de informe - Requiere autenticación"""
    return templates.TemplateResponse(
        "informe.html", {"request": request, "user": user}
    )


@router.get("/admon", response_class=HTMLResponse)
async def admin_panel(request: Request, admin: dict = Depends(require_admin)):
    """Panel de administración - Solo administradores"""
    # Obtener lista de usuarios para mostrar
    users_list = [
        {"username": username, "role": data["role"], "name": data["name"]}
        for username, data in USERS_DB.items()
    ]
    return templates.TemplateResponse(
        "admon.html", {"request": request, "user": admin, "users": users_list}
    )