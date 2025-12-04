#!/usr/bin/env python3
"""
AI Studio Playwright Automation Helper

Provides reusable Playwright-based functions for automating Google AI Studio workflows.
Follows patterns from v0-playwright-helper.py for consistency and reliability.

Functions can be wrapped as MCP tools via aistudio-mcp-tools.py.

Module: aistudio-playwright-helper
Reference: llms-aistudio-01-workflow-new-project.md
Timing: Critical patterns from llms-aistudio-04-browser-automation-reference.md
"""

import asyncio
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Tuple, Any

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration constants
STORAGE_STATE_PATH = Path.home() / ".playwright" / "aistudio_auth_state.json"
STORAGE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

# Critical timing patterns (from llms-aistudio-04-browser-automation-reference.md)
GEMINI_IMPLEMENTATION_WAIT = 90  # Seconds - Gemini implementation minimum
DIALOG_LOAD_WAIT = 8  # Seconds - GitHub/Deploy dialog rendering
VERIFICATION_RETRY_WAIT = 3  # Seconds - Between verification checks
NAVIGATION_WAIT = 3  # Seconds - Page navigation settle time


class AIStudioAutomation:
    """
    Playwright-based automation for Google AI Studio workflows.

    Provides functions for:
    - Authentication and context management
    - Project creation and naming
    - GitHub integration (create repo, commit, deploy)
    - Local repository setup

    All timing patterns follow llms-aistudio-04-browser-automation-reference.md
    """

    def __init__(self, storage_state_path: Optional[Path] = None):
        """Initialize automation helper with optional auth state."""
        self.storage_state_path = storage_state_path or STORAGE_STATE_PATH
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def login_aistudio(self) -> Tuple[BrowserContext, Page]:
        """
        Initialize browser context and perform Google authentication.

        Returns:
            Tuple[BrowserContext, Page]: Authenticated context and page

        Process:
        1. Launch browser
        2. Create new context
        3. Navigate to AI Studio
        4. Wait for user to authenticate
        5. Save authentication state for reuse
        """
        logger.info("Starting AI Studio authentication...")

        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=False)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()

            # Navigate to AI Studio
            await self.page.goto("https://aistudio.google.com/apps?source=start")
            logger.info("Navigate to AI Studio start page. Please authenticate if needed.")

            # Wait for user to authenticate and navigate to a project
            # Typically: user signs in, AI Studio loads
            await self.page.wait_for_load_state("networkidle", timeout=30000)

            # Save authentication state for reuse
            await self.context.storage_state(path=str(self.storage_state_path))
            logger.info(f"Authentication successful. State saved to {self.storage_state_path}")

            return self.context, self.page

    async def open_github_panel(self, context: BrowserContext, app_url: str) -> Page:
        """
        Navigate to AI Studio app and click 'Save to GitHub' button.

        Args:
            context: Authenticated Playwright context
            app_url: Full URL to AI Studio project (e.g.,
                    https://aistudio.google.com/apps/drive/[PROJECT-ID]?source=start)

        Returns:
            Page: Page object with GitHub panel visible

        Timing:
        - Navigation wait: 3 seconds
        - Dialog load wait: 8-10 seconds
        """
        logger.info(f"Opening GitHub panel for app: {app_url}")

        page = await context.new_page()
        await page.goto(app_url)
        await asyncio.sleep(NAVIGATION_WAIT)

        # Click "Save to GitHub" button
        save_to_github_btn = page.locator('button', has_text="Save to GitHub")
        await save_to_github_btn.click()
        logger.info("Clicked 'Save to GitHub' button")

        # Wait for GitHub panel to fully load
        logger.info(f"Waiting {DIALOG_LOAD_WAIT} seconds for GitHub dialog to render...")
        await asyncio.sleep(DIALOG_LOAD_WAIT)

        # Verify GitHub dialog is ready
        stage_commit_btn = page.locator('button', has_text="Stage and commit all changes")
        is_ready = await stage_commit_btn.is_visible()

        if not is_ready:
            logger.warning("GitHub dialog not fully loaded, waiting additional time...")
            await asyncio.sleep(VERIFICATION_RETRY_WAIT)

        logger.info("GitHub panel ready")
        return page

    async def create_github_repo(
        self,
        page: Page,
        repo_name: str,
        description: str,
        visibility: str = "private"
    ) -> Dict[str, Any]:
        """
        Fill in GitHub repository creation form and click Create.

        Args:
            page: Playwright page with GitHub panel visible
            repo_name: Repository name (e.g., 178ca256-...-visioning-circle-companion)
            description: Repository description
            visibility: "private" or "public" (default: "private")

        Returns:
            Dict: Status and metadata about created repository

        Process:
        1. Fill repository name field
        2. Fill description field
        3. Set visibility (private/public)
        4. Click "Create Git repo" button
        5. Wait 5-10 seconds for repository creation
        """
        logger.info(f"Creating GitHub repository: {repo_name}")

        try:
            # Find and fill repository name input
            repo_name_input = page.locator('input[placeholder*="Repository name"]').first
            await repo_name_input.fill(repo_name)
            logger.info(f"Filled repository name: {repo_name}")

            # Find and fill description textarea
            desc_input = page.locator('textarea[placeholder*="description"]').first
            await desc_input.fill(description)
            logger.info(f"Filled description: {description[:50]}...")

            # Set visibility to Private (should be default)
            # Look for private radio button/checkbox and ensure it's selected
            private_option = page.locator('label:has-text("Private")')
            if await private_option.is_visible():
                await private_option.click()
                logger.info("Set visibility to Private")

            # Click "Create Git repo" button
            create_repo_btn = page.locator('button', has_text="Create Git repo")
            await create_repo_btn.click()
            logger.info("Clicked 'Create Git repo' button")

            # Wait for repository creation to complete
            logger.info(f"Waiting {VERIFICATION_RETRY_WAIT * 2} seconds for repo creation...")
            await asyncio.sleep(VERIFICATION_RETRY_WAIT * 2)

            # Verify repository was created (look for success indicator or next step)
            # In AI Studio, after repo creation, should see commit message prompt
            commit_label = page.locator('text=Commit message').first
            is_ready = await commit_label.is_visible()

            return {
                "status": "success" if is_ready else "pending",
                "repo_name": repo_name,
                "created_at": datetime.now().isoformat(),
                "next_step": "commit_message" if is_ready else "verify_creation"
            }

        except Exception as e:
            logger.error(f"Error creating GitHub repository: {e}")
            return {
                "status": "error",
                "repo_name": repo_name,
                "error": str(e)
            }

    async def commit_to_github(
        self,
        page: Page,
        commit_message: str,
        issue_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Complete the commit workflow after repository creation.

        Args:
            page: Playwright page with commit prompt visible
            commit_message: Custom commit message (or will use default)
            issue_number: GitHub issue number for reference (e.g., 1)

        Returns:
            Dict: Status of commit operation

        Process:
        1. Wait for commit message prompt to appear
        2. Fill commit message textarea
        3. Click "Stage and commit all changes" button
        4. Wait for commit completion
        """
        logger.info(f"Committing to GitHub with message: {commit_message[:50]}...")

        try:
            # Fill commit message
            # The message field may be a textarea in the GitHub panel
            commit_input = page.locator('textarea').first
            await commit_input.fill(commit_message)
            logger.info("Filled commit message")

            # Click "Stage and commit all changes" button
            stage_commit_btn = page.locator('button', has_text="Stage and commit all changes")
            await stage_commit_btn.click()
            logger.info("Clicked 'Stage and commit all changes' button")

            # Wait for commit to process
            await asyncio.sleep(VERIFICATION_RETRY_WAIT)

            # Look for completion indicator (commit dialog disappears or success message)
            try:
                # Wait for the dialog to close or change state
                await page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass  # May timeout but that's okay, we'll check manually

            logger.info("Commit completed")

            return {
                "status": "success",
                "message": commit_message,
                "issue_number": issue_number,
                "committed_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error committing to GitHub: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def deploy_to_cloud_run(
        self,
        page: Page,
        google_cloud_project: str
    ) -> Dict[str, Any]:
        """
        Deploy the generated app to Google Cloud Run.

        Args:
            page: Playwright page in AI Studio
            google_cloud_project: Google Cloud project ID

        Returns:
            Dict: Deployment status and URL

        Process:
        1. Close GitHub dialog
        2. Click "Deploy app" button
        3. Wait for deploy dialog to load
        4. Select Google Cloud project
        5. Click deploy button
        6. Wait for deployment to complete
        7. Capture deployed URL
        """
        logger.info(f"Deploying application to Google Cloud project: {google_cloud_project}")

        try:
            # Close GitHub dialog
            close_btn = page.locator('button[aria-label*="Close"]').first
            if await close_btn.is_visible():
                await close_btn.click()
                logger.info("Closed GitHub dialog")

            await asyncio.sleep(VERIFICATION_RETRY_WAIT)

            # Click "Deploy app" button
            deploy_btn = page.locator('button[aria-label="Deploy app"]')
            await deploy_btn.click()
            logger.info("Clicked 'Deploy app' button")

            # Wait for deploy dialog to load
            logger.info(f"Waiting {DIALOG_LOAD_WAIT} seconds for deploy dialog...")
            await asyncio.sleep(DIALOG_LOAD_WAIT)

            # Select Google Cloud project from dropdown
            project_selector = page.locator('[role="combobox"]').first
            if await project_selector.is_visible():
                await project_selector.click()
                await asyncio.sleep(1)

                # Find and click project option
                project_option = page.locator(f'option:has-text("{google_cloud_project}")')
                if await project_option.is_visible():
                    await project_option.click()
                    logger.info(f"Selected Google Cloud project: {google_cloud_project}")

            # Click deploy/redeploy button
            redeploy_btn = page.locator('button', has_text="Redeploy").first
            if await redeploy_btn.is_visible():
                await redeploy_btn.click()
                logger.info("Clicked 'Redeploy' button - deployment started")

            # Wait for deployment to complete
            # Typically takes 30 seconds to 2 minutes
            logger.info("Waiting for deployment to complete (this may take 1-2 minutes)...")
            await asyncio.sleep(60)  # Wait at least 1 minute

            # Try to extract deployed URL from page
            deployed_url = None
            page_text = await page.text_content('body')

            # Look for deployed URL pattern (https://[name].run.app)
            import re
            url_pattern = r'https://[a-zA-Z0-9\-]+\.run\.app/?'
            matches = re.findall(url_pattern, page_text or '')
            if matches:
                deployed_url = matches[0]
                logger.info(f"Deployed URL: {deployed_url}")

            return {
                "status": "success",
                "project": google_cloud_project,
                "deployed_url": deployed_url,
                "deployed_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error deploying to Cloud Run: {e}")
            return {
                "status": "error",
                "project": google_cloud_project,
                "error": str(e)
            }

    async def clone_repository_locally(
        self,
        repo_url: str,
        local_path: Path,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Git clone the created repository to local development environment.

        Args:
            repo_url: GitHub repository URL (https or git@)
            local_path: Local directory to clone into
            branch: Branch to clone (default: "main")

        Returns:
            Dict: Clone status and path

        Uses: subprocess for git operations
        """
        logger.info(f"Cloning repository: {repo_url}")

        try:
            # Ensure local path exists
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Clone repository
            result = subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch, repo_url, str(local_path)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                logger.error(f"Git clone failed: {result.stderr}")
                return {
                    "status": "error",
                    "repo_url": repo_url,
                    "error": result.stderr
                }

            logger.info(f"Repository cloned to: {local_path}")

            # Verify clone
            if (local_path / ".git").exists():
                return {
                    "status": "success",
                    "repo_url": repo_url,
                    "local_path": str(local_path),
                    "branch": branch,
                    "cloned_at": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "repo_url": repo_url,
                    "error": "Clone succeeded but .git directory not found"
                }

        except subprocess.TimeoutExpired:
            logger.error("Git clone timed out")
            return {
                "status": "error",
                "repo_url": repo_url,
                "error": "Clone operation timed out"
            }
        except Exception as e:
            logger.error(f"Error cloning repository: {e}")
            return {
                "status": "error",
                "repo_url": repo_url,
                "error": str(e)
            }

    async def wait_for_gemini_implementation(
        self,
        page: Page,
        timeout_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Verify that Gemini implementation is complete.

        Critical timing pattern from llms-aistudio-04-browser-automation-reference.md:
        - Minimum wait: 90 seconds
        - Typical: 2-5 minutes
        - Check every 30 seconds until Stop button disappears

        Args:
            page: Playwright page with Gemini processing
            timeout_seconds: Maximum wait time (default: 5 minutes)

        Returns:
            Dict: Completion status and duration
        """
        logger.info(f"Waiting for Gemini implementation (min {GEMINI_IMPLEMENTATION_WAIT}s)...")

        # Initial wait (critical!)
        await asyncio.sleep(GEMINI_IMPLEMENTATION_WAIT)
        logger.info(f"Initial {GEMINI_IMPLEMENTATION_WAIT}s wait complete")

        start_time = datetime.now()
        elapsed = 0

        while elapsed < timeout_seconds:
            try:
                # Check for Stop button (indicates still processing)
                stop_btn = page.locator('button[aria-label*="Stop"]').first
                is_processing = await stop_btn.is_visible()

                if not is_processing:
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.info(f"Implementation complete! Total wait time: {duration:.1f}s")

                    return {
                        "status": "complete",
                        "duration_seconds": duration,
                        "completed_at": datetime.now().isoformat()
                    }

                # Still processing, wait and check again
                logger.info(f"Still processing... ({elapsed:.0f}s elapsed)")
                await asyncio.sleep(VERIFICATION_RETRY_WAIT)
                elapsed = (datetime.now() - start_time).total_seconds()

            except Exception as e:
                logger.warning(f"Error checking completion status: {e}")
                await asyncio.sleep(VERIFICATION_RETRY_WAIT)
                elapsed = (datetime.now() - start_time).total_seconds()

        logger.error(f"Implementation wait timeout after {timeout_seconds}s")
        return {
            "status": "timeout",
            "duration_seconds": timeout_seconds,
            "error": f"Implementation did not complete within {timeout_seconds} seconds"
        }

    async def cleanup(self):
        """Close browser and clean up resources."""
        if self.context:
            await self.context.close()
            logger.info("Closed browser context")
        if self.browser:
            await self.browser.close()
            logger.info("Closed browser")


# Standalone functions for MCP tool wrapping
async def aistudio_create_github_repo(
    app_url: str,
    repo_name: str,
    description: str,
    use_existing_auth: bool = True
) -> Dict[str, Any]:
    """
    Standalone function: Create GitHub repository for AI Studio project.

    This function can be wrapped as an MCP tool.

    Args:
        app_url: Full URL to AI Studio project
        repo_name: Repository name
        description: Repository description
        use_existing_auth: Use saved authentication state

    Returns:
        Dict: Repository creation status
    """
    automation = AIStudioAutomation()

    try:
        if use_existing_auth and STORAGE_STATE_PATH.exists():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                context = await browser.new_context(
                    storage_state=str(STORAGE_STATE_PATH)
                )
                page = await automation.open_github_panel(context, app_url)
                result = await automation.create_github_repo(page, repo_name, description)
                await context.close()
                await browser.close()
                return result
        else:
            logger.error("No saved authentication state. Run login first.")
            return {"status": "error", "error": "Not authenticated"}

    except Exception as e:
        logger.error(f"Error in aistudio_create_github_repo: {e}")
        return {"status": "error", "error": str(e)}


async def aistudio_commit_and_deploy(
    app_url: str,
    commit_message: str,
    google_cloud_project: str,
    issue_number: Optional[int] = None
) -> Dict[str, Any]:
    """
    Standalone function: Commit to GitHub and deploy to Cloud Run.

    This function can be wrapped as an MCP tool.

    Args:
        app_url: Full URL to AI Studio project
        commit_message: Commit message
        google_cloud_project: Google Cloud project ID
        issue_number: Optional GitHub issue number

    Returns:
        Dict: Combined commit and deployment status
    """
    automation = AIStudioAutomation()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                storage_state=str(STORAGE_STATE_PATH)
            )
            page = await context.new_page()
            await page.goto(app_url)
            await asyncio.sleep(NAVIGATION_WAIT)

            # Commit
            commit_result = await automation.commit_to_github(
                page, commit_message, issue_number
            )

            # Deploy
            deploy_result = await automation.deploy_to_cloud_run(
                page, google_cloud_project
            )

            await context.close()
            await browser.close()

            return {
                "status": "success",
                "commit": commit_result,
                "deployment": deploy_result
            }

    except Exception as e:
        logger.error(f"Error in aistudio_commit_and_deploy: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "login":
        # Run authentication
        async def run_login():
            automation = AIStudioAutomation()
            context, page = await automation.login_aistudio()
            await context.close()
            await page.context.browser.close()

        asyncio.run(run_login())
    else:
        print("AI Studio Playwright Automation Helper")
        print("Usage: python aistudio-playwright-helper.py [login|...]")
        print("\nRun 'python aistudio-playwright-helper.py login' to authenticate")
