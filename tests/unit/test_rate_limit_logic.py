import jwt
from fastapi import Request
from unittest.mock import Mock

from app.core.config import get_settings
from app.core.rate_limit import get_client_ip, get_rate_limit_key
from app.core.auth import create_access_token

settings = get_settings()


def create_mock_request(headers=None, client_host=None):
    request = Mock(spec=Request)
    request.headers = headers or {}
    if client_host:
        request.client = Mock()
        request.client.host = client_host
    else:
        request.client = None
    return request


def test_get_client_ip_no_headers():
    # 1. No headers, client is None
    req1 = create_mock_request()
    assert get_client_ip(req1) == "127.0.0.1"

    # 2. No headers, client host present
    req2 = create_mock_request(client_host="192.168.1.50")
    assert get_client_ip(req2) == "192.168.1.50"


def test_get_client_ip_x_forwarded_for():
    # X-Forwarded-For present (single IP)
    req1 = create_mock_request(
        headers={"X-Forwarded-For": "203.0.113.195"},
        client_host="127.0.0.1"
    )
    assert get_client_ip(req1) == "203.0.113.195"

    # X-Forwarded-For present (multiple IPs, select first)
    req2 = create_mock_request(
        headers={"X-Forwarded-For": "203.0.113.195, 70.41.3.18, 150.172.238.178"},
        client_host="127.0.0.1"
    )
    assert get_client_ip(req2) == "203.0.113.195"


def test_get_client_ip_x_real_ip():
    # X-Real-IP present
    req = create_mock_request(
        headers={"X-Real-IP": "198.51.100.1"},
        client_host="127.0.0.1"
    )
    assert get_client_ip(req) == "198.51.100.1"


def test_get_rate_limit_key_bearer_case_insensitive():
    email = "test@example.com"
    token = create_access_token({"sub": email})

    # Test uppercase Bearer
    req_upper = create_mock_request(
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_rate_limit_key(req_upper) == f"user:{email}"

    # Test lowercase bearer
    req_lower = create_mock_request(
        headers={"Authorization": f"bearer {token}"}
    )
    assert get_rate_limit_key(req_lower) == f"user:{email}"

    # Test invalid token falls back to IP
    req_invalid = create_mock_request(
        headers={"Authorization": "bearer invalid-token-value"},
        client_host="1.1.1.1"
    )
    assert get_rate_limit_key(req_invalid) == "ip:1.1.1.1"
