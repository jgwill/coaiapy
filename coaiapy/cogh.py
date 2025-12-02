import requests
import json
import os
from coaiapy.coaiamodule import read_config
import os

def _get_github_headers():
    config = read_config()
    token = config.get("github", {}).get("api_token") or os.getenv("GH_TOKEN")
    if not token:
        raise ValueError("GitHub token not found. Set GH_TOKEN environment variable or add it to coaia.json")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }

def list_issues(owner, repo):
    """List issues for a repository."""
    config = read_config()
    base_url = config.get("github", {}).get("base_url", "https://api.github.com")
    url = f"{base_url}/repos/{owner}/{repo}/issues"
    headers = _get_github_headers()
    response = requests.get(url, headers=headers)
    return response.text

def get_issue(owner, repo, issue_number):
    """Get a specific issue."""
    config = read_config()
    base_url = config.get("github", {}).get("base_url", "https://api.github.com")
    url = f"{base_url}/repos/{owner}/{repo}/issues/{issue_number}"
    headers = _get_github_headers()
    response = requests.get(url, headers=headers)
    return response.text

def format_issues_table(issues_json):
    """Format issues data as a readable table."""
    try:
        issues = json.loads(issues_json)
        if not issues:
            return "No issues found."

        headers = ["#", "Title", "State", "Assignee", "Labels"]
        rows = []
        for issue in issues:
            labels = ", ".join([label["name"] for label in issue.get("labels", [])])
            assignee = issue.get("assignee", {}).get("login") if issue.get("assignee") else "None"
            rows.append([
                str(issue["number"]),
                issue["title"],
                issue["state"],
                assignee,
                labels
            ])

        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if len(cell) > col_widths[i]:
                    col_widths[i] = len(cell)

        # Format table
        header_row = " | ".join([f"{h:<{col_widths[i]}}" for i, h in enumerate(headers)])
        separator = "-+-".join(["-" * w for w in col_widths])
        
        table = [header_row, separator]
        for row in rows:
            table.append(" | ".join([f"{cell:<{col_widths[i]}}" for i, cell in enumerate(row)]))
        
        return "\n".join(table)

    except json.JSONDecodeError:
        return f"Error: Could not parse issues data as JSON.\n{issues_json}"
    except Exception as e:
        return f"Error formatting issues table: {str(e)}\n\nRaw JSON:\n{issues_json}"
