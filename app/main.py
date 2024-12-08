import logging
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from app.errors import GitHubAPIError, OpenAIAPIError
from app.models import ReviewRequest
from app.redis_client import RedisClient
from app.services import fetch_github_repo, analyze_code
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Выполняется при старте приложения
    await RedisClient.get_client()
    yield
    # Выполняется при завершении приложения
    await RedisClient.close_client()


app = FastAPI(lifespan=lifespan)


@app.post("/review")
async def review_code(request: ReviewRequest):
    """
    Fetch repository contents and analyze the code.
    """
    try:
        repo_contents = await fetch_github_repo(request.github_repo_url)
        review = await analyze_code(
            repo_contents=repo_contents,
            assignment_description=request.assignment_description,
            candidate_level=request.candidate_level,
        )
        return {"review": review}
    except GitHubAPIError as e:
        logging.error(f"GitHub API error: {e.message}")
        raise HTTPException(
            status_code=e.status_code, detail=f"GitHub error: {e.message}"
        )

    except OpenAIAPIError as e:
        logging.error(f"OpenAI API error: {e.message}")
        raise HTTPException(
            status_code=e.status_code, detail=f"OpenAI error: {e.message}"
        )
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
