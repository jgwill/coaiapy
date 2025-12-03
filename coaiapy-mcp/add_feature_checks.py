#!/usr/bin/env python3
"""
Add feature config checks to all tool definitions in server.py.
"""

import re

# Read the file
with open('coaiapy_mcp/server.py', 'r') as f:
    lines = f.readlines()

output = []
i = 0

while i < len(lines):
    line = lines[i]

    # Check if this line has tool_definitions.append that's NOT already wrapped
    if 'tool_definitions.append(types.Tool(' in line:
        # Check if previous line has feature check
        if i > 0 and 'if feature_config.is_tool_enabled' in lines[i-1]:
            # Already wrapped, keep as is
            output.append(line)
            i += 1
            continue

        # Find the tool name by looking ahead
        tool_name = None
        for j in range(i, min(i + 10, len(lines))):
            match = re.search(r'name="([^"]+)"', lines[j])
            if match:
                tool_name = match.group(1)
                break

        if tool_name:
            # Get current indentation (everything before 'tool_definitions')
            indent_match = re.match(r'(\s*)', line)
            base_indent = indent_match.group(1) if indent_match else '        '

            # Add feature check line
            output.append(f'{base_indent}if feature_config.is_tool_enabled("{tool_name}"):\n')

            # Add the tool_definitions line with extra indentation
            # Replace the line to add 4 more spaces
            indented_line = line.replace(base_indent, base_indent + '    ', 1)
            output.append(indented_line)
        else:
            # Couldn't find tool name, keep original
            output.append(line)
    else:
        output.append(line)

    i += 1

# Write output
with open('coaiapy_mcp/server.py', 'w') as f:
    f.writelines(output)

print("✅ Added feature config checks to all tool definitions")
