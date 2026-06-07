from pydantic import BaseModel


class Citation(BaseModel):
    timestamp: str


class SummaryItem(BaseModel):
    text: str
    citations: list[Citation]


class DecisionItem(BaseModel):
    text: str
    citations: list[Citation]


class ActionItemAI(BaseModel):
    task: str
    assignee: str | None = None
    due_date: str | None = None
    citations: list[Citation]


class FollowUpSuggestion(BaseModel):
    text: str
    citations: list[Citation]


class MeetingAnalysisLLMResponse(BaseModel):
    summary: list[SummaryItem]
    decisions: list[DecisionItem]
    action_items: list[ActionItemAI]
    follow_ups: list[FollowUpSuggestion]
