#!/usr/bin/env python3
"""
Simple test runner for coaiapy-mcp.

Run with: python run_tests.py
"""

import sys
import subprocess

def run_tests():
    """Run pytest on the tests directory."""
    try:
        result = subprocess.run(
            ["pytest", "-v", "tests/"],
            cwd=".",
            check=False,
        )
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Install with: pip install pytest pytest-asyncio")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
