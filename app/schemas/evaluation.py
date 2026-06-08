from pydantic import BaseModel


class EvaluationResponse(BaseModel):
    candidateName: str
    email: str
    repositoryUrl: str
    deployedUrl: str
    documentationUrl: str
    externalIntegration: str
    features: list[str]
