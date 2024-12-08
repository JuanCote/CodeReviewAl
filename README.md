# CodeReviewAI

CodeReviewAI is an automated code review tool that integrates GitHub API for repository access and OpenAI's GPT for code analysis. This project provides a REST API for analyzing GitHub repositories and generating code reviews.

---

## Features

- Integration with GitHub API for repository content fetching.
- Code analysis using OpenAI GPT-4 API.
- Caching for improved performance using Redis.
- Easy setup with Poetry for dependency management.
- Docker Compose setup for Redis.

---

## Prerequisites

Ensure the following are installed on your system:

- **Python 3.10+**
- **Poetry** (Dependency management) [Install Poetry](https://python-poetry.org/docs/#installation)
- **Docker and Docker Compose**

---

## Setup Instructions

### Step 1: Clone the Repository

Clone this repository to your local machine:
```bash
git clone https://github.com/yourusername/CodeReviewAI.git
cd CodeReviewAI
```

### Step 2: Install Dependencies

Use Poetry to install all project dependencies:
```bash
poetry install
```

### Step 3: Configure Environment Variables

Create a .env file in the root directory and add the following environment variables:
```bash
GITHUB_TOKEN=your_github_token_here
OPENAI_API_KEY=your_openai_api_key_here
REDIS_URL=redis://localhost:6379
```

### Step 4: Set Up Redis with Docker Compose

Ensure Redis is running by using Docker Compose:
```bash
docker-compose up -d
```

### Step 5: Run the Application

Start the FastAPI application with:
```bash
poetry run uvicorn app.main:app --reload
```


### Scaling the Coding Assignment Auto-Review Tool

To handle 100+ review requests per minute, I would implement a task queue system like Celery, paired with a message broker such as RabbitMQ or Redis. This approach allows requests to be processed asynchronously by workers, distributing the load effectively and ensuring the backend remains responsive. For large repositories with 100+ files, I would divide the files into manageable chunks and process them incrementally. Each chunk’s analysis result would be stored temporarily in a caching system like Redis, and the final result would be compiled once all chunks are processed.

To manage the increased usage of OpenAI and GitHub APIs, I would introduce rate-limiting at the worker level to stay within API limits and implement exponential backoff strategies for retries. Additionally, repetitive results, such as already-analyzed repositories, are already being cached in the current implementation to reduce redundant API calls and minimize costs. Furthermore, if the demand increases significantly, we could explore the possibility of using multiple API keys to distribute the load across them, ensuring smooth operation and scalability.

Additionally, to prevent misuse or excessive requests from users, I would implement rate-limiting at the API level. This would restrict the number of requests a single user can make within a specific time period, ensuring fair usage and protecting the system from being overwhelmed.
