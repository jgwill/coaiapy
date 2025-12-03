#!/usr/bin/env python3
"""
Script to wrap tool definitions with feature config checks.
This reads server.py and adds conditional checks for each tool.
"""

import re

def wrap_tool_definitions(content: str) -> str:
    """Wrap each tool_definitions.append with feature config check."""

    # Pattern to match tool_definitions.append(types.Tool(...))
    # We need to find the tool name within each definition

    # First, let's find all tool definitions and wrap them
    lines = content.split('\n')
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this is a tool_definitions.append line (not already wrapped)
        if 'tool_definitions.append(types.Tool(' in line and 'if feature_config.is_tool_enabled' not in lines[max(0, i-1)]:
            # Find the tool name in the next few lines
            tool_name = None
            for j in range(i, min(i+5, len(lines))):
                name_match = re.search(r'name="([^"]+)"', lines[j])
                if name_match:
                    tool_name = name_match.group(1)
                    break

            if tool_name:
                # Get indentation of current line
                indent_match = re.match(r'(\s*)', line)
                indent = indent_match.group(1) if indent_match else '        '

                # Add the if statement before this line
                result_lines.append(f'{indent}if feature_config.is_tool_enabled("{tool_name}"):')

                # Fix indentation of the append line
                fixed_line = line.replace('tool_definitions.append(types.Tool(',
                                         '    tool_definitions.append(types.Tool(', 1)
                result_lines.append(fixed_line)
            else:
                result_lines.append(line)
        else:
            result_lines.append(line)

        i += 1

    return '\n'.join(result_lines)


if __name__ == '__main__':
    # Read server.py
    with open('/src/coaiapy/coaiapy-mcp/coaiapy_mcp/server.py', 'r') as f:
        content = f.read()

    # Wrap tools
    wrapped = wrap_tool_definitions(content)

    # Write back
    with open('/src/coaiapy/coaiapy-mcp/coaiapy_mcp/server.py', 'w') as f:
        f.write(wrapped)

    print(" Tool definitions wrapped with feature config checks")
