import logging
from datetime import datetime

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.model.standup import CommitFile, CommitStats, GitCommit

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

    def _matches_author(
        self,
        item: dict,
        github_login: str | None,
        email: str | None,
    ) -> bool:
        login = github_login.casefold() if github_login else None
        mail = email.casefold() if email else None
        commit = item.get("commit", {})
        author = commit.get("author") or {}
        github_author = item.get("author") or {}
        author_login = github_author.get("login")
        author_email = author.get("email")

        if login and author_login and author_login.casefold() != login:
            return False
        if not login and mail and author_email and author_email.casefold() != mail:
            return False
        return True

    def _commit_from_item(self, item: dict) -> GitCommit:
        commit = item.get("commit", {})
        author = commit.get("author") or {}
        stats = item.get("stats")
        files = item.get("files") or []
        return GitCommit(
            sha=item["sha"],
            message=commit.get("message", ""),
            url=item.get("html_url"),
            date=author.get("date"),
            author_name=author.get("name"),
            author_email=author.get("email"),
            stats=CommitStats.model_validate(stats) if isinstance(stats, dict) else None,
            files=[
                CommitFile(
                    filename=file_item.get("filename", ""),
                    status=file_item.get("status", "modified"),
                    additions=file_item.get("additions", 0) or 0,
                    deletions=file_item.get("deletions", 0) or 0,
                    changes=file_item.get("changes", 0) or 0,
                    patch=file_item.get("patch"),
                )
                for file_item in files
                if isinstance(file_item, dict) and file_item.get("filename")
            ],
        )

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
        shas: list[str] = []
        for item in response.json():
            if not self._matches_author(item=item, github_login=github_login, email=email):
                continue
            shas.append(item["sha"])
        for sha in shas:
            commits.append(await self.commit_detail(sha))
        return commits

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def commit_detail(self, sha: str) -> GitCommit:
        try:
            response = await self._client.get(f"/repos/{self._repo}/commits/{sha}")
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.exception("GitHub returned an error while fetching commit detail")
            raise
        except httpx.RequestError:
            logger.exception("GitHub request failed while fetching commit detail")
            raise
        return self._commit_from_item(response.json())

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def latest_commit(
        self,
        github_login: str | None,
        email: str | None,
    ) -> GitCommit | None:
        params: dict[str, str | int] = {"per_page": 20}
        if github_login:
            params["author"] = github_login

        try:
            response = await self._client.get(f"/repos/{self._repo}/commits", params=params)
            response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.exception("GitHub returned an error while fetching latest commit")
            raise
        except httpx.RequestError:
            logger.exception("GitHub request failed while fetching latest commit")
            raise

        for item in response.json():
            if self._matches_author(item=item, github_login=github_login, email=email):
                return await self.commit_detail(item["sha"])
        return None

    async def commit_url(self, sha: str) -> str:
        return f"https://github.com/{self._repo}/commit/{sha}"
