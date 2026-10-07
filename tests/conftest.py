import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.auth import cookie_transport, get_jwt_strategy
from app.database import Base, get_db
from app.models.user import User

from sqlalchemy.pool import NullPool

TEST_DATABASE_URL = "postgresql+asyncpg://andrey@localhost/dobox_test"

test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)

async def override_get_db():
  async with TestSession() as session:
    yield session

app.dependency_overrides[get_db] = override_get_db


async def create_user(email: str) -> User:
  async with TestSession() as session:
    user = User(email=email, hashed_password="not-used", is_verified=True)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def login(client: AsyncClient, user: User) -> AsyncClient:
  """Give the client a real session cookie for `user` (same JWT the app issues)."""
  token = await get_jwt_strategy().write_token(user)
  client.cookies.set(cookie_transport.cookie_name, token)
  return client


@pytest_asyncio.fixture(autouse=True)
async def reset_db():
  async with test_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  yield
  async with test_engine.begin() as conn:
    await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
  transport = ASGITransport(app=app)
  async with AsyncClient(transport=transport, base_url="http://test") as ac:
    yield ac

@pytest_asyncio.fixture
async def user():
  return await create_user("alice@example.com")

@pytest_asyncio.fixture
async def auth_client(client, user):
  return await login(client, user)
