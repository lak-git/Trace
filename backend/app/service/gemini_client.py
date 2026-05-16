import json
import logging

from google import genai
from google.genai import types

from app.model.memory import MemoryCompactResponse
from app.model.standup import GitCommit, StoredCommit

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

    async def compact_commits(
        self,
        display_name: str,
        commits: list[GitCommit],
        has_recent_commits: bool,
    ) -> tuple[list[StoredCommit], str]:
        if not commits:
            summary = (
                f"{display_name} has no commits in the standup window."
                if has_recent_commits is False
                else f"{display_name} has no commit activity to summarize."
            )
            return [], summary

        commit_lines = []
        for commit in commits:
            first_line = (commit.message or "").split("\n", maxsplit=1)[0].strip()
            commit_lines.append(
                f"- sha={commit.sha} date={commit.date} message={first_line} url={commit.url}",
            )
        prompt = (
            "Compact these Git commits into standup-ready context for a scrum assistant. "
            "Return strict JSON with keys `commits` and `activity_summary`. "
            "`commits` must be an array with one object per input commit, preserving sha, message "
            "(first line only), url, and date, and adding a 1-2 sentence `summary` of what changed. "
            "`activity_summary` is a single 2-3 sentence overview for the facilitator.\n\n"
            f"Developer: {display_name}\n"
            f"Has commits in standup window: {has_recent_commits}\n\n"
            "Commits:\n"
            + "\n".join(commit_lines)
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
            logger.exception("Gemini commit compaction failed")
            raise

        text = response.text or "{}"
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Gemini returned non-JSON commit compaction output")
            payload = {
                "commits": [
                    {
                        "sha": commit.sha,
                        "message": (commit.message or "").split("\n", maxsplit=1)[0].strip(),
                        "url": commit.url,
                        "date": commit.date.isoformat() if commit.date else None,
                        "summary": (commit.message or "").split("\n", maxsplit=1)[0].strip(),
                    }
                    for commit in commits
                ],
                "activity_summary": text.strip(),
            }

        stored: list[StoredCommit] = []
        for item, commit in zip(payload.get("commits", []), commits, strict=False):
            if not isinstance(item, dict):
                item = {}
            stored.append(
                StoredCommit(
                    sha=item.get("sha") or commit.sha,
                    message=item.get("message")
                    or (commit.message or "").split("\n", maxsplit=1)[0].strip(),
                    url=item.get("url") or commit.url,
                    date=commit.date,
                    summary=item.get("summary")
                    or (commit.message or "").split("\n", maxsplit=1)[0].strip(),
                ),
            )
        if len(stored) < len(commits):
            for commit in commits[len(stored) :]:
                stored.append(
                    StoredCommit(
                        sha=commit.sha,
                        message=(commit.message or "").split("\n", maxsplit=1)[0].strip(),
                        url=commit.url,
                        date=commit.date,
                        summary=(commit.message or "").split("\n", maxsplit=1)[0].strip(),
                    ),
                )

        activity_summary = payload.get("activity_summary")
        if not isinstance(activity_summary, str) or not activity_summary.strip():
            activity_summary = " ".join(
                item.summary for item in stored if item.summary
            ) or f"{display_name} had commit activity since the last standup."
        return stored, activity_summary.strip()
