import os
import subprocess

def get_latest_commit_files():
    """Get files modified in the latest commit."""
    try:
        # Get a list of files changed in the latest commit
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().splitlines()
        return files
    except subprocess.CalledProcessError as e:
        print(f"Error getting latest commit files: {e}")
        return []

def get_updated_lines(file_path):
    """Get updated lines from a given file in the latest commit."""
    try:
        # Use git diff to get the changed lines for the file
        result = subprocess.run(
            ["git", "diff", "-U0", "HEAD~1", "HEAD", "--", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Process the output to get only updated lines
        updated_lines = []
        for line in result.stdout.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                updated_lines.append(line[1:])  # Remove the leading "+"
        
        return updated_lines
    except subprocess.CalledProcessError as e:
        print(f"Error getting updated lines for {file_path}: {e}")
        return []

def main():
    # Get files modified in the latest commit
    files = get_latest_commit_files()
    if not files:
        print("No files were modified in the latest commit.")
        return
    
    print("Files modified in the latest commit:")
    for file in files:
        print(f"\nFile: {file}")
        
        # Get updated lines for each file
        updated_lines = get_updated_lines(file)
        if updated_lines:
            print("Updated lines:")
            for line in updated_lines:
                print(line)
        else:
            print("No updated lines found.")

if __name__ == "__main__":
    main()
