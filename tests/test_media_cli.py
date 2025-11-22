#!/usr/bin/env python
"""
Test script for CLI media commands (syntax validation)

Tests the CLI command structure and help messages:
- coaia fuse media --help
- coaia fuse media upload --help
- coaia fuse media get --help

Does NOT test actual media upload (requires Langfuse credentials).
"""
import subprocess
import sys

def test_command_help(cmd, description):
    """Test that a command shows help without errors"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print("✅ PASS - Command help displayed successfully")
            print(f"\nOutput:\n{result.stdout[:500]}")
            return True
        else:
            print(f"❌ FAIL - Command returned error code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ FAIL - Exception: {str(e)}")
        return False


def main():
    """Run CLI syntax tests"""
    print("\n" + "="*60)
    print("CLI MEDIA COMMANDS SYNTAX VALIDATION")
    print("="*60)

    tests = [
        (['coaia', 'fuse', 'media', '--help'],
         "Media subcommand help"),

        (['coaia', 'fuse', 'media', 'upload', '--help'],
         "Upload command help"),

        (['coaia', 'fuse', 'media', 'get', '--help'],
         "Get command help"),
    ]

    results = []
    for cmd, desc in tests:
        passed = test_command_help(cmd, desc)
        results.append((desc, passed))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for desc, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {desc}")

    total = len(results)
    passed_count = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed_count}/{total} tests passed")
    print("="*60)

    return 0 if passed_count == total else 1


if __name__ == "__main__":
    sys.exit(main())
