import subprocess
from langchain_ollama import OllamaLLM as Ollama
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

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
    changes = ""
    for line in result.stdout.splitlines():
        # Only consider added lines
        if line.startswith('+') and not line.startswith('+++'):
            changes += line[1:]
    return changes

def review_changes_with_llama(changed_lines):
    """Use LLaMA model from Ollama to review the updated lines."""
    # Initialize the LLaMA model through Ollama
    llm = Ollama(model="llama3.2")

    # Define a prompt template for reviewing code changes
    template = """
    Here's a text where file name seperated by an empty line with it code {code},
    Please update, optimize and resolve bugs of the code
    {format_instructions}
    """

    class Review(BaseModel):
        fileName: str = Field(description="File name")
        code: str = Field(description="Updated code")

    parser = JsonOutputParser(pydantic_object=Review)
    prompt = PromptTemplate(input_variables=["code"], template=template, partial_variables={"format_instructions": parser.get_format_instructions()})

    chain = prompt | llm | parser
    return chain.invoke(input={"code": changed_lines})

def main():
    print("Getting files modified in the latest commit...")
    modified_files = get_latest_commit_files()
    if not modified_files:
        print("No files changed in the latest commit.")
        return

    all_changes = ""
    for file_path in modified_files:
        changed_lines = get_changed_lines(file_path)
        if changed_lines:
            all_changes = "\n".join([all_changes, file_path, changed_lines])
        else:
            print("No new lines added.")
            
    if all_changes:
        # Review the changes with the LLaMA model
        print("\nReviewing changes with LLaMA 3.2 model...")
        review = review_changes_with_llama(all_changes)
        print(review)

if __name__ == "__main__":
    main()
