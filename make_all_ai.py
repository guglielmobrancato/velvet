import os

path = '/Users/guglielmobrancato-pc/Documents/GitHub/velvet/data.js'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"is_ai": false', '"is_ai": true')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
