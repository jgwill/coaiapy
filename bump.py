import re
import sys

def bump_version(file_path, new_version):
    with open(file_path, 'r') as file:
        content = file.read()

    content = re.sub(r'version\s*=\s*[\'"]([^\'"]*)[\'"]', f'version = "{new_version}"', content)
    
    with open(file_path, 'w') as file:
        file.write(content)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python bump.py <new_version>")
        sys.exit(1)

    new_version = sys.argv[1]

    files_to_update = [
        'setup.py',
        'pyproject.toml'
    ]

    for file_path in files_to_update:
        bump_version(file_path, new_version)

    print(f"Version bumped to {new_version} in {', '.join(files_to_update)}")