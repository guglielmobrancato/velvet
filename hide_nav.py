import glob
import os

files = glob.glob("/Users/guglielmobrancato-pc/Documents/GitHub/velvet/*.html")
for path in files:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        if 'href="musica.html"' in line and '<li' in line:
            continue
        if 'href="eventi.html"' in line and '<li' in line:
            continue
        new_lines.append(line)
        
    with open(path, "w", encoding="utf-8") as f:
        f.write('\n'.join(new_lines))
