import base64
import re

with open('static/img/agrosft_o.svg', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('base64,')
if idx != -1:
    end_idx = text.find('"', idx)
    b64_data = re.sub(r'\s+', '', text[idx+7:end_idx])
    missing_padding = len(b64_data) % 4
    if missing_padding:
        b64_data += '=' * (4 - missing_padding)
    with open('static/img/decoded_logo.png', 'wb') as f_out:
        f_out.write(base64.b64decode(b64_data))
    print('Decoded PNG successfully')
