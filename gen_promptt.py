import os
import re

# Configuration
DOCUMENTATION_FILE = "time_capsule_backend.md"
EXCLUDE_PATTERNS = [
    r"\.pyc$",  # Exclude Python bytecode files
    r"__pycache__",  # Exclude Python cache directories
    r"\.git",  # Exclude Git directory
    r"\.txt$",  # Exclude text files
    r"\.log$",  # Exclude log files
    "gen_prompt.py",  # Replace with the name of this script
    "gen_promptt.py",  # Replace with the name of this script
    "README.md",
    "./apikey.txt",
    "package.json",
    "package-lock.json",
    r"\.DS_Store$",  # Exclude .DS_Store files
    r"\.(jpg|jpeg|png|gif|bmp|ico)$",  # Exclude common image files
    r"\.(pdf|doc|docx|ppt|pptx|xls|xlsx)$",  # Exclude common document files
    r"\.(zip|tar|gz|rar)$",  # Exclude common archive files
    r"\.vscode",  # Exclude VS Code directory
    r"\.db$",  # Exclude database files
    r"\.PNG$",  # Exclude PNG files
    r"\.db-journal$",  # Exclude executable files
    "venv",
    "node_modules",
    "v1-0",
    "code_documentation.md",
    "complete_project.md",
    ".pytest_cache",
    "__pycache__",
    ".coverage",
    ".flake8",
    ".env",
]

EXTRA_EXCLUDE_PATTERNS = [
    "server_stress_test",
    "game_instructions.md",
    "Pipfile",
    "server_stress_test",
    "stress_tests",
    "local_sims",
    "tests",
    "routes/demo",
    "routes/agent",
    "routes/user",
]

ALLOWED_FILES = [
"docker-compose.yml",
".github/workflows/tests_coverage_deploy.yml",
"backend/tests/conftest.py",
"backend/tests/routes/admin/test_get_all_institutions.py",
"backend/tests/routes/admin/test_institution_create.py"
]

# List to track processed files
processed_files = []

# Function to generate a Markdown link for a file
def create_markdown_link(filepath, filename):
    relative_path = filepath.replace("\\", "/")  # Normalize path separators
    return f"[{filename}]({relative_path})"

# Function to process a single file
def process_file(filepath, force_include=False):
    # Skip files that match exclude patterns, unless force_include is True
    if not force_include and any(
        re.search(pattern, filepath)
        for pattern in EXCLUDE_PATTERNS + EXTRA_EXCLUDE_PATTERNS
    ):
        return ""

    try:
        # Try UTF-8 first
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            processed_files.append(filepath)  # Track successfully processed file
    except UnicodeDecodeError:
        try:
            # If UTF-8 fails, try with ISO-8859-1
            with open(filepath, "r", encoding="iso-8859-1") as f:
                content = f.read()
                processed_files.append(filepath)  # Track successfully processed file
        except UnicodeDecodeError:
            # If both fail, assume it's a binary file
            return f"### {filepath}\nUnable to read file content. It may be a binary file.\n"
    except Exception as e:
        return f"### {filepath}\nError processing file: {str(e)}\n"

    return f"### {filepath}\n```\n{content}\n```\n"

# Main function
def generate_markdown(current_folder_only=False):
    # Clear the processed files list
    processed_files.clear()

    # Delete existing documentation file if it exists
    if os.path.exists(DOCUMENTATION_FILE):
        os.remove(DOCUMENTATION_FILE)
        print(f"Deleted existing {DOCUMENTATION_FILE}")

    markdown_content = "# Project Sitemap\n\n"

    # Determine the starting directory
    start_dir = "." if current_folder_only else os.getcwd()

    for root, dirs, files in os.walk(start_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if not any(re.match(p, d) for p in EXCLUDE_PATTERNS)]

        # If current_folder_only is True, don't recurse into subdirectories
        if current_folder_only:
            dirs[:] = []

        if files:
            markdown_content += f"## {root}\n\n"
            for filename in files:
                filepath = os.path.join(root, filename)
                # Only process and add links for files that aren't excluded
                if not any(
                    re.search(pattern, filepath) for pattern in EXCLUDE_PATTERNS
                ):
                    markdown_content += create_markdown_link(filepath, filename) + "\n"
                    markdown_content += process_file(filepath)

    # Add summary of processed files at the end of the documentation
    markdown_content += "\n## Files Processed Summary\n\n"
    markdown_content += f"Total files processed: {len(processed_files)}\n\n"
    markdown_content += "### List of Processed Files:\n"
    for file in processed_files:
        markdown_content += f"- {file}\n"

    with open(DOCUMENTATION_FILE, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Generated new {DOCUMENTATION_FILE}")
    print(f"\nProcessed {len(processed_files)} files:")
    for file in processed_files:
        print(f"- {file}")

def process_allowed_files():
    """Process files from ALLOWED_FILES list that would be excluded by patterns"""
    print("\nProcessing explicitly allowed files:")
    
    # Create or append to the documentation file
    with open(DOCUMENTATION_FILE, "a", encoding="utf-8") as f:
        f.write("\n## Explicitly Allowed Files\n\n")
        
        for allowed_file in ALLOWED_FILES:
            # Use the same path format as used in os.walk()
            # Join with the project root directory (which is one level up from current directory)
            project_root = os.path.dirname(os.getcwd())  # Go up one level from backend directory
            full_path = os.path.join(project_root, allowed_file)
            
            if os.path.exists(full_path):
                # Force include the file regardless of exclusion patterns
                file_content = process_file(full_path, force_include=True)
                if file_content:
                    f.write(create_markdown_link(full_path, os.path.basename(full_path)) + "\n")
                    f.write(file_content + "\n")
                    print(f"- Added: {allowed_file}")
                else:
                    print(f"- Error processing: {allowed_file}")
            else:
                print(f"- Warning: {allowed_file} not found")

if __name__ == "__main__":
    
    # Print the current ALLOWED_FILES list
    print("\nCurrent ALLOWED_FILES:")
    for file in sorted(ALLOWED_FILES):
        print(f"- {file}")
    
    # You can change this to True to only document the current folder
    generate_markdown(current_folder_only=False)
    
    # Process files from ALLOWED_FILES list after the main documentation generation
    process_allowed_files()