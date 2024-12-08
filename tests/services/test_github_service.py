import pytest
from app.services import fetch_github_repo
from app.errors import GitHubAPIError
import httpx


@pytest.mark.asyncio(loop_scope="session")
async def test_fetch_github_repo_success(mocker):
    """Test successful fetching of GitHub repository contents."""
    mock_items = [
        {"type": "file", "path": "file1.py", "download_url": "http://mockfile1"},
        {"type": "file", "path": "file2.py", "download_url": "http://mockfile2"},
    ]
    mocker.patch(
        "httpx.AsyncClient.get",
        side_effect=[
            mocker.Mock(status_code=200, json=lambda: mock_items),
            mocker.Mock(status_code=200, text="print('Hello')"),
            mocker.Mock(status_code=200, text="print('World')"),
        ],
    )

    repo_url = "https://github.com/test/repo"
    result = await fetch_github_repo(repo_url)
    assert result == {"file1.py": "print('Hello')", "file2.py": "print('World')"}


@pytest.mark.asyncio(loop_scope="session")
async def test_fetch_github_repo_error(mocker, redis_client):
    """Test GitHub API errors."""

    mocker.patch(
        "httpx.AsyncClient.get",
        side_effect=httpx.HTTPStatusError(
            "Not found", request=mocker.Mock(), response=mocker.Mock(status_code=404)
        ),
    )

    repo_url = "https://github.com/test/repo"
    with pytest.raises(GitHubAPIError) as excinfo:
        await fetch_github_repo(repo_url)
    assert excinfo.value.status_code == 404
    assert excinfo.value.message == "Repository not found"
