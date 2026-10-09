import logging
from contextlib import asynccontextmanager

from debug_toolbar.middleware import DebugToolbarMiddleware
from fastapi import FastAPI

from app.database import engine, Base
from app.routers import items
from urllib.parse import urlencode

from fastapi import Request
from fastapi.exceptions import HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from httpx_oauth.clients.google import GoogleOAuth2
from app.auth import auth_backend, fastapi_users, oauth_backend
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, SECRET, COOKIE_SECURE, FRONTEND_URL, DEBUG


app = FastAPI(debug=DEBUG)
app.include_router(items.router)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173"],
  allow_methods=["*"],
  allow_headers=["*"],
  allow_credentials=True
)

if DEBUG:
  logger = logging.getLogger(__name__)

  app.add_middleware(
      DebugToolbarMiddleware,
      panels=["debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel"],
  )

  @app.middleware("http")
  async def log_request(request: Request, call_next):
      body = await request.body()
      logger.warning("=========== REQUEST DATA ===========")
      logger.warning("%s %s body=%s", request.method, request.url.path, body.decode())
      logger.warning("====================================")
      return await call_next(request)

@app.exception_handler(HTTPException)
async def oauth_error_handler(request: Request, exc: HTTPException):
  if request.url.path.startswith("/auth/google/callback"):
    query = urlencode({"error": str(exc.detail)})
    return RedirectResponse(f"{FRONTEND_URL}/login?{query}", status_code=302)
  return await http_exception_handler(request, exc)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])

google_client = GoogleOAuth2(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)

app.include_router(
  fastapi_users.get_oauth_router(
    google_client, oauth_backend, SECRET,
    associate_by_email=True,
    is_verified_by_default=True,
    csrf_token_cookie_secure=COOKIE_SECURE,
  ),
  prefix="/auth/google", tags=["auth"],
)
