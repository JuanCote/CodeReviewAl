import pytest
from app.services import analyze_code
from app.errors import OpenAIAPIError
import httpx


@pytest.mark.asyncio(loop_scope="session")
async def test_analyze_code_success(mocker):
    """Test successful analysis of repository contents."""
    mock_response = {
        "choices": [{"message": {"content": "Analysis completed successfully!"}}]
    }
    mocker.patch(
        "httpx.AsyncClient.post",
        return_value=mocker.Mock(status_code=200, json=lambda: mock_response),
    )

    repo_contents = {"file1.py": "print('Hello')"}
    result = await analyze_code(repo_contents, "Build a REST API", "Junior")
    assert result == "Analysis completed successfully!"


@pytest.mark.asyncio(loop_scope="session")
async def test_analyze_code_error(mocker, redis_client):
    """Test OpenAI API errors."""
    mocker.patch(
        "httpx.AsyncClient.post",
        side_effect=httpx.HTTPStatusError(
            "Unauthorized", request=mocker.Mock(), response=mocker.Mock(status_code=401)
        ),
    )

    repo_contents = {"file1.py": "print('Hello')"}
    with pytest.raises(OpenAIAPIError) as excinfo:
        await analyze_code(repo_contents, "Build a REST API", "Junior")
    assert excinfo.value.status_code == 401
    assert excinfo.value.message == "Unauthorized access to OpenAI API"
