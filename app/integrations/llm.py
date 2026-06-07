from fastapi import HTTPException
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.schemas.analysis import MeetingAnalysisLLMResponse

settings = get_settings()

client = AsyncOpenAI(
    api_key=settings.openai_api_key,
)


async def analyze_transcript(
    transcript: list[dict],
) -> MeetingAnalysisLLMResponse:
    prompt = f"""
    You are a meeting intelligence assistant.

    You analyze meeting transcripts and generate:
    1. Summary
    2. Action Items
    3. Decisions
    4. Follow-up Suggestions

    Grounding Requirements:
    - Use only information present in the transcript.
    - Do not use external knowledge.
    - Do not make assumptions.
    - Do not infer missing facts.
    - Do not create attendees, tasks, deadlines, or decisions that are not explicitly stated.
    - If a specific date cannot be determined with certainty,
    return null.

    - Only return ISO-8601 timestamps for due_date.
    Never return natural language values such as
    "Wednesday", "Thursday", "next Friday", etc.

    Citation Requirements:
    - Every generated item must contain at least one citation.
    - Citations must reference the transcript line number(s) supporting the statement.
    - Multiple citations may be used when information comes from multiple transcript segments.

    Hallucination Prevention:
    - If evidence is insufficient, return nothing for that item.
    - If an assignee is unclear, set assignee to null.
    - If a due date is unclear, set dueDate to null.
    - Never rewrite a statement into a stronger claim than what was actually said.

    Output Requirements:
    - Return valid JSON only.
    - Do not include markdown.
    - Do not include explanations.
    - Do not include fields outside the schema.

    Evaluation Priority:
    1. Factual correctness
    2. Citation accuracy
    3. Grounding
    4. Completeness

    Transcript:
    {transcript}
    """

    completion = await client.responses.parse(
        model="gpt-4.1-mini",
        input=prompt,
        text_format=MeetingAnalysisLLMResponse,
    )
    analysis = completion.output_parsed

    if analysis is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate meeting analysis",
        )

    return analysis
