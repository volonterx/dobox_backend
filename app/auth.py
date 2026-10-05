import uuid
from fastapi import Depends, Request, Response
from fastapi.responses import RedirectResponse
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, CookieTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, OAuthAccount
from app.config import SECRET, COOKIE_SECURE, FRONTEND_URL


async def get_user_db(session: AsyncSession = Depends(get_db)):
  yield SQLAlchemyUserDatabase(session, User, OAuthAccount)

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
  reset_password_token_secret = SECRET
  verification_token_secret = SECRET

  async def on_after_register(self, user, request: Request | None = None):
    print(f"User {user.email} registered.")

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

SESSION_LIFETIME = 60 * 60 * 24 * 14

cookie_transport = CookieTransport(
                       cookie_max_age=SESSION_LIFETIME,
                       cookie_secure=COOKIE_SECURE,
                       cookie_httponly=True,
                       cookie_samesite="lax",
                   )

class RedirectCookieTransport(CookieTransport):
  async def get_login_response(self, token: str) -> Response:
    response = RedirectResponse(FRONTEND_URL, status_code=302)
    return self._set_login_cookie(response, token)

redirect_cookie_transport = RedirectCookieTransport(
                       cookie_max_age=SESSION_LIFETIME,
                       cookie_secure=COOKIE_SECURE,
                       cookie_httponly=True,
                       cookie_samesite="lax",
                   )

def get_jwt_strategy():
  return JWTStrategy(secret=SECRET, lifetime_seconds=SESSION_LIFETIME)

auth_backend = AuthenticationBackend(name="cookie", transport=cookie_transport, get_strategy=get_jwt_strategy)

oauth_backend = AuthenticationBackend(
  name="oauth-cookie",
  transport=redirect_cookie_transport,
  get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
  get_user_manager, [auth_backend, oauth_backend]
)

current_active_user = fastapi_users.current_user(active=True)
