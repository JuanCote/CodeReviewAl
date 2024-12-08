import asyncio
from typing import Dict
from fastapi import HTTPException
import httpx
import os

from app.cache_utils import get_from_cache, set_to_cache
from app.errors import GitHubAPIError, OpenAIAPIError

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


async def fetch_github_repo(repo_url: str) -> Dict[str, str]:
    """
    Fetch the contents of all files in a GitHub repository.

    :param repo_url: The URL of the GitHub repository.
    :return: A dictionary with file paths as keys and file contents as values.
    :raises GitHubAPIError: If there are issues with the GitHub API (e.g., 404, 401).
    """
    try:
        cache_key = f"repo:{repo_url}"
        cached_data = await get_from_cache(cache_key)
        if cached_data:
            return cached_data

        headers = {"Authorization": f"token {GITHUB_TOKEN}"}

        repo_url = str(repo_url)

        api_url = (
            repo_url.replace("https://github.com/", "https://api.github.com/repos/")
            + "/contents"
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
            response.raise_for_status()
            items = response.json()

            if not isinstance(items, list):
                raise GitHubAPIError(500, "Unexpected response format from GitHub API")

            files_content = {}
            for item in items:
                if item["type"] == "file":  # Process only files
                    file_response = await client.get(
                        item["download_url"], headers=headers
                    )
                    file_response.raise_for_status()
                    files_content[item["path"]] = file_response.text

            await set_to_cache(cache_key, files_content)

            return files_content
    except httpx.HTTPStatusError as e:
        if e.response and e.response.status_code == 404:
            raise GitHubAPIError(404, "Repository not found")
        elif e.response and e.response.status_code == 401:
            raise GitHubAPIError(401, "Unauthorized access to GitHub API")
        raise GitHubAPIError(500, "Unknown GitHub API error")


async def analyze_code(
    repo_contents: Dict[str, str], assignment_description: str, candidate_level: str
) -> str:
    """
    Analyze the repository contents using OpenAI API.

    :param repo_contents: A dictionary with file paths as keys and file contents as values.
    :param assignment_description: The description of the assignment.
    :param candidate_level: The candidate's level (Junior, Middle, or Senior).
    :return: The analysis result as a string.
    :raises OpenAIAPIError: If there are issues with the OpenAI API or the response.
    """

    cache_key = f"analysis:{hash(str(repo_contents))}:{assignment_description}:{candidate_level}"

    cached_analysis = await get_from_cache(cache_key)
    if cached_analysis:
        return cached_analysis

    prompt = f"""
    Analyze the following repository for a {candidate_level} level assignment:
    Assignment Description: {assignment_description}
    
    Repository Contents:
    {''.join([f'File: {name}\n{content}\n' for name, content in repo_contents.items()])}

    Provide a detailed review with:
    - Found files
    - Downsides/Comments
    - Rating
    - Conclusion
    """
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    data = {"model": "gpt-4-turbo", "messages": [{"role": "user", "content": prompt}]}

    try:

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions", headers=headers, json=data
            )
            response.raise_for_status()

            try:
                content = response.json()["choices"][0]["message"]["content"]
                await set_to_cache(cache_key, content)
                return content
            except (KeyError, ValueError):
                raise OpenAIAPIError(500, "Unexpected response format from OpenAI API")

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise OpenAIAPIError(401, "Unauthorized access to OpenAI API")
        elif e.response.status_code == 400:
            raise OpenAIAPIError(400, "Bad request to OpenAI API")
        raise OpenAIAPIError(500, "Error communicating with OpenAI API")

    except httpx.ReadTimeout:
        raise OpenAIAPIError(504, "OpenAI API request timed out")

    except Exception as e:
        raise OpenAIAPIError(500, f"Unexpected error: {str(e)}")
