import logging
from datetime import datetime

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.model.standup import GitCommit

logger = logging.getLogger(__name__)


class GitHubClient:
    def __init__(self, token: str, repo: str) -> None:
        self._repo = repo
        self._client = httpx.AsyncClient(
            base_url="https://api.github.com",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=20,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def commits_since(
        self,
        github_login: str | None,
        email: str | None,
        since: datetime | None,
    ) -> list[GitCommit]:
        params: dict[str, str] = {}
        if since:
            params["since"] = since.isoformat()

        try:
            response = await self._client.get(f"/repos/{self._repo}/commits", params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.exception("GitHub returned an error while fetching commits")
            raise
        except httpx.RequestError:
            logger.exception("GitHub request failed while fetching commits")
            raise

        commits: list[GitCommit] = []
        login = github_login.casefold() if github_login else None
        mail = email.casefold() if email else None
        for item in response.json():
            commit = item.get("commit", {})
            author = commit.get("author") or {}
            github_author = item.get("author") or {}
            author_login = github_author.get("login")
            author_email = author.get("email")

            if login and author_login and author_login.casefold() != login:
                continue
            if not login and mail and author_email and author_email.casefold() != mail:
                continue

            commits.append(
                GitCommit(
                    sha=item["sha"],
                    message=commit.get("message", ""),
                    url=item.get("html_url"),
                    date=author.get("date"),
                    author_name=author.get("name"),
                    author_email=author_email,
                ),
            )
        return commits

    async def commit_url(self, sha: str) -> str:
        return f"https://github.com/{self._repo}/commit/{sha}"
