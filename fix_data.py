import json

with open('/Users/guglielmobrancato-pc/Documents/GitHub/velvet/data.js', 'r') as f:
    text = f.read()
data_str = text.split("const mshData = ")[1].strip().rstrip(";")
data = json.loads(data_str)

for section in data:
    for item in data[section]:
        author = item.get("author", "")
        if "AI" in author or "Xantus" in author or "Synth Shaman" in author:
            item["is_ai"] = True
        else:
            item["is_ai"] = False

with open('/Users/guglielmobrancato-pc/Documents/GitHub/velvet/data.js', 'w') as f:
    f.write("const mshData = " + json.dumps(data, indent=4) + ";\n")
