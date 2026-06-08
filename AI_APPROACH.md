# AI Analysis Approach

## Prompt Design & Structured Output

IntelliMeeter leverages OpenAI's structured output capabilities to ensure that AI-generated insights are reliable and valid. The model is constrained by Pydantic schemas to extract:

1. **Summaries**: High-level overview of the discussion.
2. **Decisions**: Explicit conclusions reached during the meeting.
3. **Action Items**: Discrete tasks with assignees and due dates.
4. **Follow-ups**: Suggestions for future exploration.

## Citation Strategy (Grounding)

To combat hallucinations, the system employs a strict citation requirement:
* Every generated insight must be linked to a `timestamp` from the original transcript.
* This ensures that every claim made by the AI can be verified by a human user by referring back to the source audio/text.

## Hallucination Prevention

1. **Transcript-Only Context**: The system prompt strictly forbids the use of external knowledge.
2. **Explicit Negation**: The model is instructed to return `null` or empty lists if evidence for a claim is insufficient.
3. **Pydantic Validation**: All output is validated against schemas that require specific formats (like ISO-8601 for dates).

## Process Flow

1. **Transcript Submission**: User submits a meeting with a timestamped transcript.
2. **Analysis Trigger**: The analysis service prepares a context-heavy prompt for OpenAI.
3. **Structured Extraction**: The LLM processes the transcript and returns a Pydantic-validated JSON object.
4. **Persistence**: The summary and decisions are saved to the `MeetingAnalysis` table, while `ActionItem` records are created individually for tracking.
