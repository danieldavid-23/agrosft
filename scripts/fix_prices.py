import os
import re

directories = ['apps', 'templates']
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # regex to find ${{ var|floatformat:2 }} and replace with {{ var|currency_cop }}
    # We must handle spaces carefully.
    content = re.sub(r'\$\{\{\s*(.*?)\|floatformat:2\s*\}\}', r'{{ \1|currency_cop }}', content)
    
    # Sometimes it might not have the $ sign in front, but it's a price.
    # So we look for {{ var|floatformat:2 }} where var has 'precio', 'total', 'subtotal'
    def replace_no_dollar(match):
        var = match.group(1)
        if any(keyword in var.lower() for keyword in ['precio', 'total', 'subtotal']):
            return f'{{{{ {var}|currency_cop }}}}'
        return match.group(0)
    
    content = re.sub(r'\{\{\s*(.*?)\|floatformat:2\s*\}\}', replace_no_dollar, content)
    
    if content != original_content:
        # Need to ensure {% load currency_tags %} is in the file
        if '{% load currency_tags %}' not in content:
            # Insert it after extends or at the top
            extends_match = re.search(r'\{%\s*extends\s+.*?%\}', content)
            if extends_match:
                end_pos = extends_match.end()
                content = content[:end_pos] + '\n{% load currency_tags %}' + content[end_pos:]
            else:
                content = '{% load currency_tags %}\n' + content
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {filepath}")

for d in directories:
    dir_path = os.path.join(base_dir, d)
    if os.path.exists(dir_path):
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.html'):
                    process_file(os.path.join(root, file))

print("Done.")
