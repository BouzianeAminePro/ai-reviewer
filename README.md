# Git Commit File Tracker

This project provides a Python script that retrieves files modified in the latest Git commit and displays the updated lines for each file. It is designed to be used in Continuous Integration (CI) environments, such as GitHub Actions and GitLab CI.

## Features

- Get a list of files modified in the latest commit.
- Retrieve updated lines for each modified file.
- Easy integration with CI/CD pipelines.

## Prerequisites

- Docker
- Git

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
