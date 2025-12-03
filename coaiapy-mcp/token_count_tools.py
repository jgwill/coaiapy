import ast
import tiktoken
from pathlib import Path

enc = tiktoken.get_encoding('cl100k_base')
f = Path('coaiapy-mcp/coaiapy_mcp/tools.py')
src = f.read_text()
tree = ast.parse(src)
results = []
for node in tree.body:
    if isinstance(node, ast.AsyncFunctionDef):
        doc = ast.get_docstring(node) or ''
        tokens = len(enc.encode(doc))
        results.append(f'* {node.name} {tokens}')
print('\n'.join(results))
