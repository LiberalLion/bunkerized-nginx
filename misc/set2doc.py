#!/usr/bin/python3

import json

with open("settings.json") as f :
	data = json.loads(f.read())

with open("docs/environment_variables.md") as f :
	docs = f.read()

output = ""
for cat in data:
	for param in data[cat]["params"]:
		params = param["params"] if param["type"] == "multiple" else [param]
		for true_param in params:
			if true_param["env"] not in docs:
				print(
					f"Missing variable in category {cat} : "
					+ true_param["env"]
					+ "="
					+ true_param["default"]
				)
