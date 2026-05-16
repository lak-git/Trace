import json
import logging

from google import genai
from google.genai import types

from app.model.memory import MemoryCompactResponse

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, api_key: str, model: str, max_output_tokens: int) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model
        self._max_output_tokens = max_output_tokens

    async def compact_standup_segment(self, transcript: str) -> MemoryCompactResponse:
        prompt = (
            "Compact this daily scrum transcript segment into a concise memory entry. "
            "Return strict JSON with keys `summary` and `importance` where importance is 1, 2, or 3. "
            "Use importance=3 only for blockers, escalations, or delivery risk; importance=2 for notable progress/decisions; importance=1 for routine updates.\n\n"
            f"Transcript:\n{transcript}"
        )
        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=self._max_output_tokens,
                    response_mime_type="application/json",
                ),
            )
        except Exception:
            logger.exception("Gemini compaction failed")
            raise

        text = response.text or "{}"
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Gemini returned non-JSON compaction output")
            payload = {"summary": text.strip(), "importance": 1}
        return MemoryCompactResponse.model_validate(payload)
