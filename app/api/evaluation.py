from fastapi import APIRouter

from app.schemas.evaluation import EvaluationResponse

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.get("", response_model=EvaluationResponse)
async def get_evaluation_metadata():
    return {
        "candidateName": "Shreyansh Pandey",
        "repositoryUrl": "https://github.com/shreyansh232/intellimeeter",
        "deployedUrl": "https://intellimeeter.onrender.com",
        "documentationUrl": "https://intellimeeter.onrender.com/docs",
        "externalIntegration": "Discord (Overdue Action Item Notifications)",
        "features": [
            "Secure Authentication (JWT, pwdlib Argon2/Bcrypt)",
            "Meeting Management (Create, Retrieve, List)",
            "LLM-Powered Meeting Analysis (Summary, Decisions, Action Items)",
            "Automated Action Item Tracking",
            "Async Database Support (PostgreSQL, SQLAlchemy)",
            "Automated CI/CD (GitHub Actions)",
            "Comprehensive Test Suite (Unit & Integration)",
            "Standardized API Responses (Success/Error wrappers, Trace IDs)",
            "Developer Experience (Makefile, modern uv package management)",
        ],
    }
