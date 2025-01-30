import pytest
from httpx import AsyncClient
from app.main import app
from app.database import get_session, init_db
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as Session
from sqlalchemy.orm import sessionmaker
from app.models import CachedResult

DATABASE_URL = "sqlite+aiosqlite:///:memory:"  # Use an in-memory DB for testing

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
TestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="function")
async def test_db():
    async with engine.begin() as conn:
        await conn.run_sync(CachedResult.metadata.create_all)

    session = TestingSessionLocal()
    yield session
    await session.close()


@pytest.fixture(scope="function")
async def client(test_db):
    app.dependency_overrides[get_session] = lambda: test_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# 🔹 Test Valid Input
@pytest.mark.asyncio
async def test_valid_payload(client):
    response = await client.post("/payload", json={
        "list_1": ["first string", "second string"],
        "list_2": ["other string", "another string"]
    })
    assert response.status_code == 200
    assert "id" in response.json()


# 🔹 Test Cache Hit (same input should return same ID)
@pytest.mark.asyncio
async def test_cache_hit(client):
    payload = {"list_1": ["test"], "list_2": ["data"]}

    first_response = await client.post("/payload", json=payload)
    second_response = await client.post("/payload", json=payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["id"] == second_response.json()["id"]  # Cache Hit


# 🔹 Test Unequal List Lengths
@pytest.mark.asyncio
async def test_invalid_list_length(client):
    response = await client.post("/payload", json={
        "list_1": ["one", "two"],
        "list_2": ["only one"]
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Lists must be of the same length."


# 🔹 Test Empty Lists
@pytest.mark.asyncio
async def test_empty_list(client):
    response = await client.post("/payload", json={
        "list_1": [],
        "list_2": []
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Lists cannot be empty."


# 🔹 Test Payload Not Found
@pytest.mark.asyncio
async def test_payload_not_found(client):
    response = await client.get("/payload/invalid_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Payload not found."


# 🔹 Test Different Inputs Return Different IDs
@pytest.mark.asyncio
async def test_different_inputs_return_different_ids(client):
    response1 = await client.post("/payload", json={
        "list_1": ["foo"],
        "list_2": ["bar"]
    })
    response2 = await client.post("/payload", json={
        "list_1": ["different"],
        "list_2": ["values"]
    })

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json()["id"] != response2.json()["id"]  # Should be different


# 🔹 Test Getting Valid Payload
@pytest.mark.asyncio
async def test_get_valid_payload(client):
    post_response = await client.post("/payload", json={
        "list_1": ["valid"],
        "list_2": ["test"]
    })

    payload_id = post_response.json()["id"]
    get_response = await client.get(f"/payload/{payload_id}")

    assert get_response.status_code == 200
    assert "output" in get_response.json()
