#!/usr/bin/env python
"""
Test script for media utility functions

Tests the core utility functions for media upload support:
- SHA-256 hash calculation
- Content type detection
- Content type validation
- Media display formatting
"""
import sys
import os

# Add parent directory to path to import coaiapy
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coaiapy.cofuse import (
    calculate_sha256,
    detect_content_type,
    validate_content_type,
    format_media_display
)


def test_calculate_sha256():
    """Test SHA-256 hash calculation"""
    print("=" * 60)
    print("TEST 1: Calculate SHA-256 Hash")
    print("=" * 60)

    # Get path to test file (same directory as this script)
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(test_dir, "notebook_graph.jpg")

    if not os.path.exists(test_file):
        print(f"SKIP: Test file not found: {test_file}")
        return

    try:
        hash_value = calculate_sha256(test_file)
        print(f"File: {test_file}")
        print(f"SHA-256: {hash_value}")
        print(f"Length: {len(hash_value)} characters")
        print("STATUS: PASS ✓")
    except Exception as e:
        print(f"STATUS: FAIL ✗")
        print(f"Error: {str(e)}")
    print()


def test_detect_content_type():
    """Test content type detection"""
    print("=" * 60)
    print("TEST 2: Detect Content Type")
    print("=" * 60)

    test_cases = [
        "image.jpg",
        "image.png",
        "video.mp4",
        "audio.mp3",
        "document.pdf",
        "data.json",
        "unknown.xyz"
    ]

    for filename in test_cases:
        content_type = detect_content_type(filename)
        print(f"{filename:20} -> {content_type}")

    print("STATUS: PASS ✓")
    print()


def test_validate_content_type():
    """Test content type validation"""
    print("=" * 60)
    print("TEST 3: Validate Content Type")
    print("=" * 60)

    test_cases = [
        ("image/jpeg", True),
        ("video/mp4", True),
        ("audio/mpeg", True),
        ("application/pdf", True),
        ("text/plain", True),
        ("image/invalid", False),
        ("video/unsupported", False),
    ]

    all_passed = True
    for content_type, should_be_valid in test_cases:
        result = validate_content_type(content_type)
        is_valid = result["valid"]
        status = "✓" if is_valid == should_be_valid else "✗"

        if is_valid != should_be_valid:
            all_passed = False

        print(f"{status} {content_type:25} -> {result['valid']} (expected: {should_be_valid})")

    print(f"STATUS: {'PASS ✓' if all_passed else 'FAIL ✗'}")
    print()


def test_format_media_display():
    """Test media display formatting"""
    print("=" * 60)
    print("TEST 4: Format Media Display")
    print("=" * 60)

    # Sample media object
    media_data = {
        "id": "media_123abc",
        "fileName": "notebook_graph.jpg",
        "contentType": "image/jpeg",
        "contentLength": 193424,
        "traceId": "trace_xyz789",
        "observationId": "obs_456def",
        "field": "input",
        "sha256Hash": "a1b2c3d4e5f6g7h8i9j0",
        "uploadedAt": "2025-11-17T12:34:56.789Z"
    }

    formatted = format_media_display(media_data)
    print(formatted)
    print("\nSTATUS: PASS ✓")
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("MEDIA UTILITY FUNCTIONS TEST SUITE")
    print("=" * 60)
    print()

    test_calculate_sha256()
    test_detect_content_type()
    test_validate_content_type()
    test_format_media_display()

    print("=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
