import subprocess
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def get_latest_commit_files():
    """Get files changed in the latest commit."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        stdout=subprocess.PIPE,
        text=True
    )
    files = result.stdout.strip().splitlines()
    return files

def get_changed_lines(file_path):
    """Get changed lines in a file between the latest and the previous commit."""
    result = subprocess.run(
        ["git", "diff", "HEAD~1", "HEAD", "--", file_path],
        stdout=subprocess.PIPE,
        text=True
    )
    changes = []
    for line in result.stdout.splitlines():
        # Only consider added lines
        if line.startswith('+') and not line.startswith('+++'):
            changes.append(line[1:])
    return changes

def review_changes_with_llama(changed_lines):
    """Use LLaMA model from Ollama to review the updated lines."""
    # Initialize the LLaMA model through Ollama
    llm = Ollama(model="llama3.2")

    # Define a prompt template for reviewing code changes
    template = """
    Please provide only the updated code from the following changes without any additional text, and the code not in a markdown close:
    {code}
    """

    # Use LangChain's prompt and chain functionality to generate a response
    prompt = PromptTemplate(input_variables=["code"], template=template)
    chain = LLMChain(llm=llm, prompt=prompt)

    # Join changed lines as a single string to pass into the LLM
    code_to_review = "\n".join(changed_lines)
    review = chain.run(code=code_to_review)

    return review

def main():
    print("Getting files modified in the latest commit...")
    modified_files = get_latest_commit_files()
    if not modified_files:
        print("No files changed in the latest commit.")
        return

    all_changes = []
    for file_path in modified_files:
        print(f"\nChanges in {file_path}:")
        changed_lines = get_changed_lines(file_path)
        if changed_lines:
            all_changes.extend(changed_lines)
            for line in changed_lines:
                print(line)
        else:
            print("No new lines added.")

    if all_changes:
        # Review the changes with the LLaMA model
        print("\nReviewing changes with LLaMA 3.2 model...")
        review = review_changes_with_llama(all_changes)
        print("\nModel Review:")
        print(review)

if __name__ == "__main__":
    main()
