#!/usr/bin/env python3
import os
import re
import subprocess
import json
from collections import defaultdict
import sys

LLMS_DIR = "/src/llms"

def get_all_llms_files_and_names():
    """Returns a list of tuples (absolute_path, prompt_name) for all llms-*.txt and llms-*.md files."""
    llms_data = []
    for filename in os.listdir(LLMS_DIR):
        if (filename.startswith("llms-") and filename.endswith(".txt")) or \
           (filename.startswith("llms-") and filename.endswith(".md")):
            file_path = os.path.join(LLMS_DIR, filename)
            prompt_name = os.path.splitext(filename)[0]
            llms_data.append((file_path, prompt_name))
    return llms_data

def get_transformed_content_and_dependencies(file_path, original_content, all_llms_filenames):
    """
    Calls transform_llms_content.py to get transformed content and dependencies.
    """
    process = subprocess.run(
        ["python3", os.path.join(LLMS_DIR, "transform_llms_content.py")],
        input=original_content,
        capture_output=True,
        text=True
    )
    if process.returncode != 0:
        print(f"Error transforming content for {file_path}: {process.stderr}", file=sys.stderr)
        return None, []
    
    try:
        result = json.loads(process.stdout)
        return result["transformed_content"], result["dependencies"]
    except json.JSONDecodeError:
        print(f"Error decoding JSON from transform_llms_content.py for {file_path}: {process.stdout}", file=sys.stderr)
        return None, []

def topological_sort(graph):
    """
    Performs a topological sort on the dependency graph.
    Returns a tuple of (sorted_nodes, cycled_nodes).
    If no cycles exist, cycled_nodes will be empty.
    """
    in_degree = defaultdict(int)
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1

    queue = [node for node in graph if in_degree[node] == 0]
    sorted_order = []

    while queue:
        node = queue.pop(0)
        sorted_order.append(node)

        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    cycled_nodes = [node for node in graph if node not in sorted_order]
    return sorted_order, cycled_nodes

def sync_llms_ordered():
    llms_data = get_all_llms_files_and_names()
    all_llms_filenames = [os.path.basename(fp) for fp, pn in llms_data]
    
    graph = defaultdict(list)
    file_contents_map = {}
    transformed_contents_map = {}
    dependencies_map = {}

    # First pass: get all transformed content and build dependency graph
    for file_path, prompt_name in llms_data:
        with open(file_path, 'r') as f:
            original_content = f.read()
        file_contents_map[prompt_name] = original_content

        transformed_content, dependencies = get_transformed_content_and_dependencies(
            file_path, original_content, all_llms_filenames
        )
        if transformed_content is None:
            print(f"Skipping {prompt_name} due to transformation error.", file=sys.stderr)
            continue

        transformed_contents_map[prompt_name] = transformed_content
        dependencies_map[prompt_name] = dependencies
        
        # Add nodes to graph even if they have no dependencies
        if prompt_name not in graph: # Ensure all nodes are in the graph
            graph[prompt_name] = []

        for dep in dependencies:
            # Only add dependency if the dependent prompt actually exists as a file
            if dep in [pn for fp, pn in llms_data]:
                graph[dep].append(prompt_name)
            else:
                print(f"Warning: Prompt '{prompt_name}' depends on '{dep}', but '{dep}' does not exist as a local LLMS file. This dependency will be ignored for ordering.", file=sys.stderr)

    # Perform topological sort
    sorted_prompts, cycled_nodes = topological_sort(graph)

    # Report cycle information if any cycles exist
    if cycled_nodes:
        print(f"Warning: Graph has a cycle involving nodes: {', '.join(cycled_nodes)}. Check for circular dependencies in your LLMS files.", file=sys.stderr)
        print(f"Proceeding to sync {len(sorted_prompts)} acyclic prompts...", file=sys.stderr)

    # Second pass: process prompts in sorted order
    for prompt_name in sorted_prompts:
        file_path = next((fp for fp, pn in llms_data if pn == prompt_name), None)
        if not file_path:
            print(f"Error: Could not find file path for prompt '{prompt_name}'. Skipping.", file=sys.stderr)
            continue

        transformed_content = transformed_contents_map.get(prompt_name)
        if transformed_content is None:
            print(f"Error: Transformed content not found for prompt '{prompt_name}'. Skipping.", file=sys.stderr)
            continue

        print(f"Processing {os.path.basename(file_path)}...")

        # Fetch current prompt content from coaia fuse
        get_command = ["coaia", "fuse", "prompts", "get", prompt_name, "-c"]
        current_prompt_process = subprocess.run(get_command, capture_output=True, text=True)
        current_prompt_content = current_prompt_process.stdout.strip()

        if transformed_content.strip() == current_prompt_content.strip():
            print(f"No changes detected for prompt: {prompt_name}. Skipping update.")
        else:
            print(f"Changes detected for prompt: {prompt_name}. Updating...")
            # Call coaia fuse prompts create with the transformed content
            command = [
                "coaia", "fuse", "prompts", "create",
                prompt_name,
                "--commit-message", "Automated sync with Langfuse references (ordered)",
                "--type", "text" # Assuming all are text prompts
            ]
            
            # Pass content via stdin
            process = subprocess.run(command, input=transformed_content, capture_output=True, text=True)
            
            if process.returncode == 0:
                print(f"Successfully synced prompt: {prompt_name}")
            else:
                print(f"Failed to sync prompt: {prompt_name}")
                print(f"Stderr: {process.stderr}")
                print(f"Stdout: {process.stdout}")

if __name__ == "__main__":
    sync_llms_ordered()
