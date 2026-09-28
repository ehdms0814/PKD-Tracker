import re

def strip_code(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Remove multi-line docstrings """ ... """
    code = re.sub(r'"""[\s\S]*?"""', '', code)
    
    # 2. Remove single-line comments that start with #
    lines = code.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith('#'):
            continue
        
        # Find inline comments, but be careful with colors like '#2ca02c'
        # Only remove if it has a space before the #
        if ' #' in line:
            line = line.split(' #')[0]
            
        cleaned_lines.append(line)
        
    # Clean up excessive newlines
    final_code = '\n'.join(cleaned_lines)
    final_code = re.sub(r'\n\s*\n', '\n\n', final_code)
    
    # Ensure it doesn't start with excessive newlines
    final_code = final_code.lstrip()

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(final_code)

files = ['main.py', 'data_manager.py', 'analyzer_visualizer.py']
for file in files:
    strip_code(file)
    print(f"Stripped {file}")
