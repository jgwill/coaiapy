import re
import sys

def bump_version(file_path, new_version):
    with open(file_path, 'r') as file:
        content = file.read()

    content = re.sub(r'version\s*=\s*[\'\"]([^\'\"]*)[\'\"]', f'version = "{new_version}"', content)

    with open(file_path, 'w') as file:
        file.write(content)


def get_current_version(file_path):
    with open(file_path, 'r') as file:
        match = re.search(r'version\s*=\s*[\'\"]([^\'\"]*)[\'\"]', file.read())
        return match.group(1) if match else "0.0.0"


def increment_patch(version):
    parts = version.split('.')
    if len(parts) == 3 and parts[-1].isdigit():
        parts[-1] = str(int(parts[-1]) + 1)
    else:
        parts.append('1')
    return '.'.join(parts)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        new_version = sys.argv[1]
    else:
        current = get_current_version('pyproject.toml')
        new_version = increment_patch(current)

    files_to_update = [
        'setup.py',
        'pyproject.toml'
    ]

    for file_path in files_to_update:
        bump_version(file_path, new_version)

    print(f"Version bumped to {new_version} in {', '.join(files_to_update)}")
