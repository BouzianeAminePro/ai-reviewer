import os
import subprocess
import time
import re
import sqlite3
import pickle
import logging

from langchain_ollama.llms import OllamaLLM as Ollama

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GITHUB_REF = os.getenv("GITHUB_REF", "refs/pull/2/merge")
IGNORED_FILES = os.getenv("IGNORED_FILES", ["README.md", ".gitignore", "requirements.txt"])

CACHE_DB = 'cache.db'
CACHE_EXPIRY = 3600
PR_NUMBER = int(re.search(r'refs/pull/(\d+)/merge', GITHUB_REF).group(1)) if re.search(r'refs/pull/(\d+)/merge', GITHUB_REF) else None

llm = Ollama(model=os.getenv("OLLAMA_MODEL", "qwen2.5-coder:latest"), base_url=os.getenv("OLLAMA_API_BASE_URL", "http://localhost:11434"))

def init_cache_db():
    """Initialize the SQLite database for caching."""
    with sqlite3.connect(CACHE_DB) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                data BLOB,
                timestamp REAL
            )
        ''')

def cache_data(key, data):
    """Cache data in SQLite."""
    with sqlite3.connect(CACHE_DB) as conn:
        conn.execute('REPLACE INTO cache (key, data, timestamp) VALUES (?, ?, ?)', 
                     (key, pickle.dumps(data), time.time()))

def fetch_from_cache(key):
    """Retrieve data from the cache."""
    with sqlite3.connect(CACHE_DB) as conn:
        result = conn.execute('SELECT data, timestamp FROM cache WHERE key = ?', (key,)).fetchone()
    return result

def get_cached_data(key, fetch_function, *args):
    """Fetch data with caching mechanism."""
    cached_entry = fetch_from_cache(key)
    if cached_entry and (time.time() - cached_entry[1]) < CACHE_EXPIRY:
        return pickle.loads(cached_entry[0])
    data = fetch_function(*args)
    cache_data(key, data)
    return data

def fetch_github_data(command):
    """Fetch data using Git command."""
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise Exception(f"Git Command Error: {result.stderr}")
    return result.stdout

def get_repository():
    """Retrieve repository data."""
    return fetch_github_data(['git', 'remote', '-v'])

def get_pull_request(pr_number):
    """Retrieve pull request data."""
    logging.info(f"Fetching pull request {pr_number}...")
    fetch_github_data(['git', 'fetch', 'origin', f'pull/{pr_number}/head:pr-{pr_number}'])
    logging.info(f"Successfully fetched pull request {pr_number}.")

def get_pull_request_files(pr_number):
    """Retrieve pull request file data."""
    logging.info(f"Fetching files for pull request {pr_number}...")
    fetch_github_data(['git', 'fetch', 'origin', f'pull/{pr_number}/head:pr-{pr_number}'])
    files = fetch_github_data(['git', 'diff', '--name-status', f'origin/main...pr-{pr_number}'])
    logging.info(f"Successfully fetched files for pull request {pr_number}.")
    return files

def get_pr_diff(pr_number):
    """Fetch and format the pull request diff."""
    files = get_pull_request_files(pr_number)
    if not files:
        print(f"No files found for pull request {pr_number}.")
        return None
    return fetch_github_data(['git', 'diff', f'origin/main...pr-{pr_number}'])

def parse_diff(diff):
    """Parse the Git diff output to extract modified lines."""
    updates = {}
    current_file = None

    for line in diff.split("\n"):
        if line.startswith("diff --git"):
            current_file = line.split(" b/")[-1]
            if current_file in IGNORED_FILES:
                logging.info(f"Ignoring file: {current_file}")
                current_file = None
                continue
            updates[current_file] = []
            logging.info(f"Processing file: {current_file}")
        elif line.startswith("@@"):
            current_line = parse_chunk_header(line)
        elif line.startswith("+") and not line.startswith("+++"):
            if current_file and line[1:].strip() and not line[1:].strip().startswith("#") and not line[1:].strip() in ['{', '}', 'import', '(', ')'] and not line.startswith("from "):
                updates[current_file].append((current_line, line[1:]))
                current_line += 1
    return updates

def parse_chunk_header(header):
    """Extract line number from chunk header."""
    match = re.search(r'@@ -\d+,\d+ \+(\d+)', header)
    return int(match.group(1)) if match else 0

def propose_updates(file_changes):
    """Generate suggestions for modified lines."""
    suggestions = {}
    for file, changes in file_changes.items():
        suggestions[file] = []
        logging.info(f"Generating suggestions for file: {file}")
        
        current_group = []

        for line_num, line in changes:
            if line.strip() == "":
                continue

            if current_group and line_num != current_group[-1][0] + 1:
                # If the current line is not consecutive, process the current group
                add_suggestion(suggestions[file], current_group)
                current_group = []

            current_group.append((line_num, line))
            logging.info(f"Processing line {line_num} in {file}: {line}")

        # Process any remaining lines in the last group
        if current_group:
            add_suggestion(suggestions[file], current_group)

    return suggestions

def add_suggestion(suggestions, current_group):
    """Generate and add suggestion for the current group of lines."""
    prompt = f"Review the following lines and suggest improvements only if necessary and primordial and give out only the code nothing more and don't review comments, imports or require, if there's none please write only NOTHING ! : {''.join(l[1] for l in current_group)}"
    suggestion = llm.invoke(prompt)
    if suggestion.strip() != 'NOTHING!':
        suggestions.append({
            "line_number": current_group[0][0],  # Use the first line number of the group
            "lines": [l[1] for l in current_group],
            "suggestion": suggestion
        })
    logging.info(f"Suggestion for lines {current_group[0][0]}-{current_group[-1][0]}: {suggestion}")

def add_comments_to_pr(pr_number, comments):
    """Add comments to a pull request."""
    logging.info(f"Adding comments to pull request {pr_number}...")
    files = get_pull_request_files(pr_number).splitlines()

    for file, suggestions in comments.items():
        file_patch = next((f.split()[1] for f in files if f.split()[1] == file), None)
        if not file_patch:
            logging.warning(f"Patch not found for {file}.")
            continue

        for suggestion in suggestions:
            try:
                body = f"This is a suggestion for improvement: \n\n {suggestion['suggestion']}"
                line_number = suggestion['line_number']
                subprocess.run(['gh', 'pr', 'comment', str(pr_number), '--body', body], check=True)
                logging.info(f"Comment added for {file} at line {line_number}: {suggestion['suggestion']}")
            except Exception as e:
                logging.error(f"Error adding comment for {file} at line {line_number}: {e}")

# Main Function
def main():
    try:
        # init_cache_db()
        diff = get_pr_diff(PR_NUMBER)
        if not diff:
            print("Failed to fetch diff.")
            return

        changes = parse_diff(diff)
        suggestions = propose_updates(changes)
        add_comments_to_pr(PR_NUMBER, suggestions)
        print("Comments added successfully.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    init_cache_db()
    main()
