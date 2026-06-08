import pytest
from httpx import AsyncClient
from app.core.rate_limit import limiter

@pytest.fixture(autouse=True)
def reset_limiter():
    limiter._storage.reset()
    yield
    limiter._storage.reset()

@pytest.mark.asyncio
async def test_rate_limiting_register(client: AsyncClient):
    email_template = "rate_limit_{}@example.com"
    password = "securepassword"

    responses = []
    # Register has a limit of 5/minute. Let's make 6 calls.
    for i in range(6):
        response = await client.post(
            "/api/auth/register",
            json={"email": email_template.format(i), "password": password}
        )
        responses.append(response)

    status_codes = [r.status_code for r in responses]
    print(f"Register status codes: {status_codes}")
    # The 6th response should be 429 if rate limiting works.
    assert 429 in status_codes

@pytest.mark.asyncio
async def test_rate_limiting_authenticated(client: AsyncClient):
    email = "rate_limit_auth@example.com"
    password = "securepassword"

    # Register & Login
    reg_resp = await client.post(
        "/api/auth/register",
        json={"email": email, "password": password}
    )
    assert reg_resp.status_code == 200

    login_response = await client.post(
        "/api/auth/login",
        json={"email": email, "password": password}
    )
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Let's call /api/meetings (POST) which has limit of 30/minute.
    # We will make 31 calls.
    responses = []
    meeting_data = {
        "title": "Meeting Title",
        "meeting_date": "2026-06-06T12:00:00Z",
        "participants": [email],
        "transcript": [{"timestamp": "00:01", "speaker": "AI", "text": "Hello world"}],
    }
    for _ in range(31):
        response = await client.post(
            "/api/meetings",
            headers=headers,
            json=meeting_data
        )
        responses.append(response)

    status_codes = [r.status_code for r in responses]
    print(f"Auth status codes: {status_codes}")
    assert 429 in status_codes
