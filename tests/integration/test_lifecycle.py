import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from app.schemas.analysis import (
    ActionItemAI,
    Citation,
    DecisionItem,
    FollowUpSuggestion,
    MeetingAnalysisLLMResponse,
    SummaryItem,
)


@pytest.fixture
def mock_llm_response():
    return MeetingAnalysisLLMResponse(
        summary=[
            SummaryItem(text="Test Summary", citations=[Citation(timestamp="00:01")])
        ],
        decisions=[
            DecisionItem(text="Test Decision", citations=[Citation(timestamp="00:02")])
        ],
        follow_ups=[
            FollowUpSuggestion(
                text="Test Follow-up", citations=[Citation(timestamp="00:03")]
            )
        ],
        action_items=[
            ActionItemAI(
                task="Overdue Task",
                assignee="lifecycle@example.com",
                due_date=datetime.now(UTC) - timedelta(days=1),
                citations=[Citation(timestamp="00:04")],
            )
        ],
    )


@pytest.mark.asyncio
async def test_full_lifecycle(client: AsyncClient, mock_llm_response):
    email = "lifecycle@example.com"
    password = "securepassword"

    # 1. Register
    register_response = await client.post(
        "/api/auth/register", json={"email": email, "password": password}
    )
    assert register_response.status_code == 200
    user_data = register_response.json()
    assert user_data["email"] == email

    # 2. Login
    login_response = await client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    token = token_data["access_token"]

    auth_headers = {"Authorization": f"Bearer {token}"}

    # 3. Create Meeting
    meeting_data = {
        "title": "Integration Test Meeting",
        "meeting_date": "2026-06-06T12:00:00Z",
        "participants": [email],
        "transcript": [{"timestamp": "00:01", "speaker": "AI", "text": "Hello world"}],
    }
    create_response = await client.post(
        "/api/meetings", headers=auth_headers, json=meeting_data
    )
    assert create_response.status_code == 201
    meeting_resp_data = create_response.json()
    meeting = meeting_resp_data["data"]
    meeting_id = meeting["id"]

    # 4. Analyze Meeting (Mocked LLM)
    with patch(
        "app.services.analysis.analyze_transcript", return_value=mock_llm_response
    ):
        analyze_response = await client.post(
            f"/api/meetings/{meeting_id}/analyze", headers=auth_headers
        )
        assert analyze_response.status_code == 200
        # Analysis response is wrapped in SuccessResponse by the service/route
        analysis_data = analyze_response.json()["data"]
        assert "summary" in analysis_data

    # 5. Query Overdue Action Items
    overdue_response = await client.get(
        "/api/action-items/overdue", headers=auth_headers
    )
    assert overdue_response.status_code == 200
    overdue_resp_data = overdue_response.json()
    # It uses success_response
    overdue_items = overdue_resp_data["data"]
    assert len(overdue_items) > 0
    assert overdue_items[0]["task"] == "Overdue Task"
