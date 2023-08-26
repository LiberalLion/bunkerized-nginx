#!/usr/bin/python3

import json

with open("settings.json") as f :
	data = json.loads(f.read())

output = ""
for cat in data:
	output += f"# {cat}" + "\n"
	for param in data[cat]["params"]:
		params = param["params"] if param["type"] == "multiple" else [param]
		for true_param in params :
			output += "#" + true_param["env"] + "=" + true_param["default"] + "\n"
	output += "\n"
print(output)
