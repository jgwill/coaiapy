#!/usr/bin/env python3
"""
AI Studio MCP Tools Server - Production Ready

Uses FastMCP (current modelcontextprotocol SDK) with decorator pattern.
Exposes AI Studio Playwright automation functions as MCP tools.

Install: pip install mcp playwright

Usage in .mcp.json:
{
  "mcpServers": {
    "aistudio": {
      "command": "python",
      "args": ["/path/to/aistudio_mcp_tools.py"]
    }
  }
}
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

from aistudio_playwright_helper import (
    AIStudioAutomation,
    STORAGE_STATE_PATH,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP(name="aistudio")


@mcp.tool()
async def aistudio_login() -> dict:
    """Authenticate to Google AI Studio and save session state."""
    logger.info("Starting AI Studio authentication...")
    try:
        automation = AIStudioAutomation()
        context, page = await automation.login_aistudio()

        await context.storage_state(path=str(STORAGE_STATE_PATH))
        await context.close()
        await page.context.browser.close()

        return {
            "status": "success",
            "message": f"Authenticated to AI Studio. Session saved to {STORAGE_STATE_PATH}",
            "storage_state_path": str(STORAGE_STATE_PATH)
        }
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def aistudio_create_repo(
    app_url: str,
    repo_name: str,
    description: str,
    visibility: str = "private"
) -> dict:
    """Create GitHub repository for AI Studio project."""
    logger.info(f"Creating repository: {repo_name}")
    try:
        from aistudio_playwright_helper import aistudio_create_github_repo

        result = await aistudio_create_github_repo(
            app_url=app_url,
            repo_name=repo_name,
            description=description,
            use_existing_auth=True
        )
        logger.info(f"Repository creation result: {result}")
        return result
    except Exception as e:
        logger.error(f"Repository creation failed: {e}")
        return {
            "status": "error",
            "repo_name": repo_name,
            "error": str(e)
        }


@mcp.tool()
async def aistudio_commit_and_deploy(
    app_url: str,
    commit_message: str,
    google_cloud_project: str,
    issue_number: Optional[int] = None
) -> dict:
    """Commit to GitHub and deploy to Cloud Run."""
    logger.info(f"Committing and deploying to {google_cloud_project}")
    try:
        from aistudio_playwright_helper import aistudio_commit_and_deploy

        result = await aistudio_commit_and_deploy(
            app_url=app_url,
            commit_message=commit_message,
            google_cloud_project=google_cloud_project,
            issue_number=issue_number
        )
        logger.info(f"Commit and deploy result: {result}")
        return result
    except Exception as e:
        logger.error(f"Commit and deploy failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@mcp.tool()
async def aistudio_clone_repository(
    repo_url: str,
    local_path: str,
    branch: str = "main"
) -> dict:
    """Clone GitHub repository locally."""
    logger.info(f"Cloning {repo_url} to {local_path}")
    try:
        from aistudio_playwright_helper import AIStudioAutomation

        automation = AIStudioAutomation()
        result = await automation.clone_repository_locally(
            repo_url=repo_url,
            local_path=Path(local_path),
            branch=branch
        )
        logger.info(f"Clone result: {result}")
        return result
    except Exception as e:
        logger.error(f"Clone failed: {e}")
        return {
            "status": "error",
            "repo_url": repo_url,
            "error": str(e)
        }


@mcp.tool()
async def aistudio_wait_for_implementation(
    app_url: str,
    timeout_seconds: int = 300
) -> dict:
    """Wait for Gemini implementation to complete."""
    logger.info(f"Waiting for implementation (max {timeout_seconds}s)")
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                storage_state=str(STORAGE_STATE_PATH)
            )
            page = await context.new_page()
            await page.goto(app_url)

            automation = AIStudioAutomation()
            result = await automation.wait_for_gemini_implementation(
                page=page,
                timeout_seconds=timeout_seconds
            )

            await context.close()
            await browser.close()

            logger.info(f"Implementation wait result: {result}")
            return result
    except Exception as e:
        logger.error(f"Wait for implementation failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

@mcp.tool()
async def aistudio_send_prompt(
    app_url: str,
    prompt_text: str,
    timeout_seconds: int = 120
) -> dict:
    """Sends a prompt to the AI Studio UI."""
    logger.info(f"Sending prompt to AI Studio: {prompt_text[:80]}...")
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                storage_state=str(STORAGE_STATE_PATH)
            )
            page = await context.new_page()
            await page.goto(app_url, wait_until="networkidle")

            # More robust selector for the textarea
            prompt_textarea_selector = "textarea[aria-label='Make changes, add new features, ask for anything']"
            await page.wait_for_selector(prompt_textarea_selector, timeout=30000)
            
            # Clear the textarea before filling
            await page.evaluate(f"document.querySelector('{prompt_textarea_selector}').value = ''")
            await page.fill(prompt_textarea_selector, prompt_text)

            # Click the send button
            send_button_selector = "button[aria-label='Send']"
            await page.click(send_button_selector)
            
            await asyncio.sleep(2) # Wait a moment for the UI to update

            # Verify the prompt was sent by checking the last message
            last_message_selector = "div.user-query .message-content"
            await page.wait_for_selector(last_message_selector, timeout=15000)
            
            last_message_text = await page.locator(last_message_selector).last.inner_text()

            if prompt_text.strip() in last_message_text.strip():
                status = "success"
                message = "Prompt sent and verified in chat history."
            else:
                status = "warning"
                message = "Prompt was sent, but verification in chat history failed."

            await context.close()
            await browser.close()

            return {"status": status, "message": message}

    except Exception as e:
        logger.error(f"Sending prompt failed: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    logger.info("Starting AI Studio MCP Tools Server")
    logger.info("Available tools: aistudio_login, aistudio_create_repo, aistudio_commit_and_deploy, aistudio_clone_repository, aistudio_wait_for_implementation, aistudio_send_prompt")
    mcp.run()
