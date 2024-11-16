# Git Commit File Tracker

This project provides a Python script that retrieves files modified in the latest Git commit and displays the updated lines for each file, along with a review of the code with the updates. It is designed to be used in Continuous Integration (CI) environments, such as GitHub Actions and GitLab CI.

## Features

- Get a list of files modified in the latest commit.
- Retrieve updated lines for each modified file.
- Review code changes using the LLaMA model from Ollama.
- Easy integration with CI/CD pipelines.
- **New:** Automatically reviews changes with the LLaMA 3.2 model after retrieving updated lines.

## Prerequisites

- Docker
- Git
- Python 3.11 or higher (for local testing)

## Setup

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Build the Docker image:**

   ```bash
   docker build -t git-commit-file-tracker .
   ```

3. **Run the Docker container:**

   ```bash
   docker run --rm git-commit-file-tracker
   ```

## Usage in CI/CD

### GitHub Actions

You can use the following example workflow to integrate this script into your GitHub Actions:

```yaml
name: CI

on:
  push:
    branches:
      - main

jobs:
  track-commits:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Build and run Docker container
        run: |
          docker build -t git-commit-file-tracker .
          docker run --rm git-commit-file-tracker
```

### GitLab CI

For GitLab CI, you can add the following configuration to your `.gitlab-ci.yml` file:

```yaml
stages:
  - track

track_commits:
  stage: track
  image: python:3.11
  before_script:
    - apt-get update && apt-get install -y git
  script:
    - python main.py
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

```yaml
name: LLM Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  code_review:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'

    - name: Install dependencies
      run: |
        pip install requests langchain_core

    - name: Run code review script
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        OLLAMA_API_KEY: ${{ secrets.OLLAMA_API_KEY }}
      run: python .github/scripts/llm_code_review.py
```
