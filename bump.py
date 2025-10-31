import re
import sys
import os
import argparse

def bump_version(file_path, new_version):
    """Update version string in a file."""
    if not os.path.exists(file_path):
        print(f"Skipping {file_path} (not found)")
        return False

    with open(file_path, 'r') as file:
        content = file.read()

    # Handle both version = "x.y.z" and __version__ = "x.y.z"
    updated = re.sub(r'(__|)version(__|)\s*=\s*[\'\"]([^\'\"]*)[\'\"]',
                     lambda m: f'{m.group(1)}version{m.group(2)} = "{new_version}"',
                     content)

    if updated != content:
        with open(file_path, 'w') as file:
            file.write(updated)
        return True
    return False


def get_current_version(file_path):
    """Extract current version from a file."""
    if not os.path.exists(file_path):
        return "0.0.0"

    with open(file_path, 'r') as file:
        match = re.search(r'(__|)version(__|)\s*=\s*[\'\"]([^\'\"]*)[\'\"]', file.read())
        return match.group(3) if match else "0.0.0"


def increment_patch(version):
    """Increment the patch version number."""
    parts = version.split('.')
    if len(parts) == 3 and parts[-1].isdigit():
        parts[-1] = str(int(parts[-1]) + 1)
    else:
        parts.append('1')
    return '.'.join(parts)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bump version in Python package files')
    parser.add_argument('version', nargs='?', help='New version number (e.g., 1.2.3)')
    parser.add_argument('--package', help='Package name (e.g., coaiapy-mcp)')
    args = parser.parse_args()

    # Determine the base directory and package name
    script_dir = os.path.dirname(os.path.abspath(__file__))

    if args.package:
        # For coaiapy-mcp: coaiapy-mcp/pyproject.toml and coaiapy-mcp/coaiapy_mcp/__init__.py
        # Construct the absolute path to the package directory
        base_dir = os.path.join(script_dir, args.package)
        package_name = args.package.replace('-', '_')
    else:
        # For coaiapy: pyproject.toml and coaiapy/__init__.py
        base_dir = script_dir # For coaiapy, base_dir is the script's directory
        package_name = 'coaiapy'

    # Get or increment version
    pyproject_path = os.path.join(base_dir, 'pyproject.toml')
    if args.version:
        new_version = args.version
    else:
        current = get_current_version(pyproject_path)
        new_version = increment_patch(current)

    # Define files to update
    files_to_update = [
        os.path.join(base_dir, 'setup.py'),
        pyproject_path,
        os.path.join(base_dir, package_name, '__init__.py')
    ]

    # Update files
    updated_files = []
    for file_path in files_to_update:
        if bump_version(file_path, new_version):
            updated_files.append(file_path)

    if updated_files:
        print(f"✅ Version bumped to {new_version} in:")
        for f in updated_files:
            print(f"   - {f}")
    else:
        print(f"⚠️  No files were updated")
