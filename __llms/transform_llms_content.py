import os
import re
import sys
import json

LLMS_DIR = "/src/llms"

def get_all_llms_filenames():
    """Returns a list of all llms-*.txt and llms-*.md filenames."""
    llms_filenames = []
    for filename in os.listdir(LLMS_DIR):
        if (filename.startswith("llms-") and filename.endswith(".txt")) or \
           (filename.startswith("llms-") and filename.endswith(".md")):
            llms_filenames.append(filename)
    return llms_filenames

def transform_content_with_langfuse_references(original_content, all_llms_filenames):
    """
    Replaces llms-*.txt or llms-*.md references in content with Langfuse prompt syntax.
    Returns the modified content and a list of discovered dependencies.
    """
    modified_content = original_content
    dependencies = []
    
    # Regex to find @@@langfusePrompt:name=<prompt_name>|label=latest@@@ patterns
    langfuse_ref_pattern = r'@@@langfusePrompt:name=([a-zA-Z0-9_.-]+)\|label=latest@@@'

    for other_filename in all_llms_filenames:
        prompt_name = os.path.splitext(other_filename)[0]
        
        # This pattern should match the full filename including .txt or .md within backticks
        pattern = r'`' + re.escape(other_filename) + r'`'
        replacement = f"@@@langfusePrompt:name={prompt_name}|label=latest@@@"

        # Find dependencies before replacement
        # Check if the current other_filename is referenced in the original content
        if re.search(pattern, original_content):
            dependencies.append(prompt_name)

        new_modified_content, num_sub = re.subn(pattern, replacement, modified_content)
        if num_sub > 0:
            modified_content = new_modified_content
            
    # Also find dependencies that might already be in Langfuse format
    for match in re.finditer(langfuse_ref_pattern, modified_content):
        dep_name = match.group(1)
        if dep_name not in dependencies:
            dependencies.append(dep_name)

    return modified_content, dependencies

if __name__ == "__main__":
    original_content = sys.stdin.read()
    all_llms_filenames = get_all_llms_filenames()
    transformed_content, dependencies = transform_content_with_langfuse_references(original_content, all_llms_filenames)
    
    result = {
        "transformed_content": transformed_content,
        "dependencies": dependencies
    }
    print(json.dumps(result))
