from fastapi.testclient import TestClient
from app.main import app
from app.errors import GitHubAPIError, OpenAIAPIError

client = TestClient(app)


def test_review_success(mocker):
    """Test the /review endpoint for a successful request."""
    mocker.patch(
        "app.main.fetch_github_repo",
        return_value={"file1.py": "print('Hello')"},
    )
    mocker.patch(
        "app.main.analyze_code",
        return_value="Analysis completed successfully!",
    )

    response = client.post(
        "/review",
        json={
            "github_repo_url": "https://github.com/test/repo",
            "assignment_description": "Build a REST API",
            "candidate_level": "Junior",
        },
    )
    assert response.status_code == 200
    assert response.json() == {"review": "Analysis completed successfully!"}
