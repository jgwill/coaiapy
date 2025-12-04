import argparse
import asyncio
import os
import json
from playwright.async_api import async_playwright, TimeoutError

# The config file is expected in the Current Working Directory
CONFIG_PATH = os.path.join(os.getcwd(), "v0_config.json")

# The auth state is stored relative to the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_STATE_PATH = os.path.join(SCRIPT_DIR, "v0_auth_state.json")

def load_config():
    """Loads the configuration from the JSON file in the CWD."""
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Configuration file not found in the current directory: {CONFIG_PATH}")
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

async def login_v0():
    """Opens a browser for manual login and saves the session state."""
    print("Starting login process...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("Navigating to v0.app...")
        await page.goto("https://v0.app")
        
        print("*****************************************************************")
        print("BROWSER OPENED. PLEASE LOG IN MANUALLY (e.g., using your Passkey).")
        print("The script will wait for 2 minutes for you to complete the login.")
        print("*****************************************************************")

        try:
            await page.get_by_role("link", name="Projects").wait_for(state="visible", timeout=120000)
            print("Login successful!")
            print(f"Saving authentication state to {STORAGE_STATE_PATH}...")
            await context.storage_state(path=STORAGE_STATE_PATH)
            print("Authentication state saved successfully.")
        except TimeoutError:
            print("Login was not completed within the 2-minute time limit.")
        finally:
            print("Closing browser.")
            await browser.close()

async def git_pull_changes(context, config):
    """Automates the git pull process using an authenticated context."""
    page = await context.new_page()
    try:
        print(f"Navigating to {config['v0_chat_url']} for git pull...")
        await page.goto(config['v0_chat_url'])
        await page.get_by_role("button", name="Synced to main").wait_for(state="visible", timeout=60000)
        print("Clicking 'Synced to main' button...")
        await page.get_by_role("button", name="Synced to main").click()
        print("Clicking 'Pull Changes' button...")
        await page.get_by_role("button", name="Pull Changes").click()
        await page.get_by_text("Syncing Changes").wait_for(state="hidden", timeout=120000)
        print("Git pull changes completed successfully.")
    finally:
        await page.close()

async def publish_changes(context, config):
    """Automates the publish process using an authenticated context."""
    page = await context.new_page()
    try:
        print(f"Navigating to {config['v0_chat_url']} for publishing...")
        await page.goto(config['v0_chat_url'])
        await page.get_by_role("button", name="Publish").wait_for(state="visible", timeout=60000)
        print("Clicking 'Publish' dropdown button...")
        await page.get_by_role("button", name="Publish").click()
        await page.wait_for_timeout(1000)

        publish_changes_option = page.get_by_text("Publish Changes")
        update_option = page.get_by_role("button", name="Update")

        if await publish_changes_option.is_visible():
            print("'Publish Changes' option is visible. Clicking it...")
            await publish_changes_option.click()
            await page.get_by_text("Publishing...").wait_for(state="visible", timeout=60000)
            print("Publishing in progress...")
            await page.get_by_text("Publishing...").wait_for(state="hidden", timeout=180000)
            print("Publishing completed successfully.")
        elif await update_option.is_visible():
            print("'Update' button is visible, which means changes are already published.")
            print("Publish step considered successful.")
        else:
            await page.screenshot(path="publish_error_snapshot.png")
            raise Exception("Could not find 'Publish Changes' or 'Update' in the publish dropdown. See snapshot.")
    finally:
        await page.close()

async def view_app(context, config):
    """Opens the production URL in a new tab."""
    page = await context.new_page()
    print(f"Opening production app at {config['production_app_url']}...")
    await page.goto(config['production_app_url'])
    print("App opened. Browser will remain open for 1 minute.")
    await page.wait_for_timeout(60000)
    await page.close()

async def main():
    parser = argparse.ArgumentParser(description="v0 Deployer. Looks for v0_config.json in the current directory.")
    parser.add_argument("--login-v0", action="store_true", help="Open browser to save auth state for v0.dev")
    parser.add_argument("--deploy", action="store_true", help="Perform git pull and then publish changes.")
    parser.add_argument("--view", action="store_true", help="View the production application after deployment.")
    parser.add_argument("--profile-path", type=str, help="Path to a persistent chromium user profile.")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed mode (default)")
    parser.add_argument("--headless", action="store_false", dest="headed", help="Run browser in headless mode")
    parser.set_defaults(headed=True)
    args = parser.parse_args()

    if args.login_v0:
        await login_v0()
        return

    if not (args.deploy or args.view):
        parser.print_help()
        return

    config = load_config()
    context_manager = None

    async with async_playwright() as p:
        try:
            if args.profile_path:
                print(f"Using persistent profile from: {args.profile_path}")
                if not os.path.isdir(args.profile_path):
                    raise FileNotFoundError(f"Profile path not found: {args.profile_path}")
                context = await p.chromium.launch_persistent_context(args.profile_path, headless=not args.headed)
            else:
                if not os.path.exists(STORAGE_STATE_PATH):
                    raise FileNotFoundError(f"Authentication file not found at {STORAGE_STATE_PATH}. Please run --login-v0 first.")
                browser = await p.chromium.launch(headless=not args.headed)
                context = await browser.new_context(storage_state=STORAGE_STATE_PATH)
            
            context_manager = context

            if args.deploy:
                print("--- Starting Deployment ---")
                # Create a new context for each step to ensure isolation
                print("\nStep 1: Pulling Git Changes...")
                pull_context = await context.browser.new_context(storage_state=STORAGE_STATE_PATH if not args.profile_path else None)
                await git_pull_changes(pull_context, config)
                await pull_context.close()

                print("\nStep 2: Publishing Changes...")
                publish_context = await context.browser.new_context(storage_state=STORAGE_STATE_PATH if not args.profile_path else None)
                await publish_changes(publish_context, config)
                await publish_context.close()

                print("--- Deployment Finished ---")
                if args.view:
                    print("\nStep 3: Opening Production App...")
                    view_context = await context.browser.new_context(storage_state=STORAGE_STATE_PATH if not args.profile_path else None)
                    await view_app(view_context, config)
                    await view_context.close()

            elif args.view:
                 await view_app(context, config)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if context_manager:
                print("Closing browser context.")
                await context_manager.close()

if __name__ == "__main__":
    print("Script starting...")
    asyncio.run(main())
