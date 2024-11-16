import os
from langchain.llms import Ollama
from github import Github
import subprocess

# Setup environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_IDENTIFIER = os.getenv("GITHUB_REPOSITORY_ID", "ai-reviewer")
PR_NUMBER = 123  # Replace with the pull request number

# Initialize GitHub client
github_client = Github(GITHUB_TOKEN)
repo = github_client.get_repo(REPO_IDENTIFIER)

# Initialize LangChain with Ollama
llm = Ollama(model="qwen2.5-coder:latest", api_base=os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434"))  # Adjust if necessary

def get_pr_diff(pr_number):
    """Get the diff for a pull request."""
    try:
        result = subprocess.run(
            ["gh", "pr", "diff", str(pr_number)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise Exception(result.stderr)
        return result.stdout
    except Exception as e:
        print(f"Error fetching diff: {e}")
        return None

def parse_diff(diff):
    """Parse the Git diff output to extract modified lines."""
    updates = {}
    current_file = None

    for line in diff.split("\n"):
        if line.startswith("diff --git"):
            current_file = line.split(" b/")[-1]
            updates[current_file] = []
        elif line.startswith("+") and not line.startswith("+++"):
            updates[current_file].append(line[1:])  # Exclude the "+" sign
    return updates

def propose_updates(file_changes):
    """Generate suggestions for each modified line."""
    suggestions = {}
    for file, lines in file_changes.items():
        suggestions[file] = []
        for line in lines:
            prompt = f"Review the following line and suggest improvements if any:\n{line}"
            suggestion = llm(prompt)
            suggestions[file].append({
                "line": line,
                "suggestion": suggestion.strip(),
            })
    return suggestions

def add_comments_to_pr(pr_number, comments):
    """
    Add comments to a pull request for each updated line separately.
    """
    pr = repo.get_pull(pr_number)

    # Retrieve the PR's files and diff details to locate exact line positions
    files = pr.get_files()

    for file, suggestions in comments.items():
        # Fetch file-specific patch data
        file_patch = next((f.patch for f in files if f.filename == file), None)

        if not file_patch:
            print(f"Could not find patch for file {file}. Skipping...")
            continue

        # Parse the diff to find positions
        file_diff_lines = file_patch.split("\n")
        diff_line_map = {}
        current_line_in_file = 0

        for diff_line in file_diff_lines:
            if diff_line.startswith("@@"):
                # Parse chunk header (e.g., @@ -12,7 +13,8 @@)
                parts = diff_line.split()
                # Extract the new file line range (e.g., `+13,8`)
                new_file_info = parts[2]
                start_line = int(new_file_info.split(",")[0][1:])
                current_line_in_file = start_line - 1  # Reset tracking
            elif diff_line.startswith("+") and not diff_line.startswith("+++"):
                current_line_in_file += 1
                diff_line_map[current_line_in_file] = diff_line[1:]  # Map line number to content

        # Post comments for each suggestion
        for suggestion in suggestions:
            for line_num, line_content in diff_line_map.items():
                if suggestion['line'].strip() == line_content.strip():
                    body = f"**Suggestion for line:** `{line_content}`\n\n{suggestion['suggestion']}"
                    pr.create_review_comment(body, file, None, position=line_num)
                    print(f"Comment added for {file} at line {line_num}.")
                    break

# Main function
def main():
    # Fetch PR diff
    diff = get_pr_diff(PR_NUMBER)
    if not diff:
        print("Failed to fetch diff.")
        return

    # Parse changes
    changes = parse_diff(diff)

    # Propose updates
    suggestions = propose_updates(changes)

    # Add comments to PR
    add_comments_to_pr(PR_NUMBER, suggestions)
    print("Comments added successfully.")

if __name__ == "__main__":
    main()
