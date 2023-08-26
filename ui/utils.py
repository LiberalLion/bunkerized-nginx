#!/usr/bin/python3

import datetime, re, json, os

def get_variables():
	vars = {
		"DOCKER_HOST": "unix:///var/run/docker.sock",
		"API_URI": "",
		"ABSOLUTE_URI": "",
		"FLASK_SECRET": os.urandom(32),
		"ADMIN_USERNAME": "admin",
		"ADMIN_PASSWORD": "changeme",
	}
	for k in vars :
		if k in os.environ :
			vars[k] = os.environ[k]
	return vars

def log(event):
	with open("/var/log/nginx/ui.log", "a") as f:
		f.write(
			f"[{str(datetime.datetime.now().replace(microsecond=0))}] {event}" + "\n"
		)

def env_to_summary_class(var, value):
	if type(var) is list and type(value) is list :
		for i in range(0, len(var)) :
			if not isinstance(var[i], str) :
				continue
			if re.search(value[i], var[i]) :
				return "check text-success"
		return "times text-danger"
	if not isinstance(var, str) :
		return "times text-danger"
	return "check text-success" if re.search(value, var) else "times text-danger"

def form_service_gen(id, label, type, value, name):
	pt = ""
	if type == "checkbox":
		checked = "checked" if value == "yes" else ""
		input = f'<div class="form-check form-switch"><input type="{type}" class="form-check-input" id="{id}" name="{name}" {checked}></div>'
		pt = "pt-0"
	elif type == "text":
		input = f'<input type="{type}" class="form-control" id="{id}" value="{value}" name="{name}">'
	return f'<label for="{id}" class="col-4 col-form-label {pt}">{label}</label><div class="col-8">{input}</div>'

def form_service_gen_multiple(id, label, params):
	buttons = '<button class="btn btn-success" type="button" onClick="addMultiple(\'%s\', \'%s\');"><i class="fas fa-plus"></i> Add</button> <button class="btn btn-danger" type="button" onClick="delMultiple(\'%s\', \'%s\')"><i class="fas fa-trash"></i> Del</button>' % (id, json.dumps(params).replace("\"", "&quot;"), id, json.dumps(params).replace("\"", "&quot;"))
	return f'<label for="{id}-btn" class="col-4 col-form-label mb-3">{label}</label><div class="col-8 mb-3" id="{id}-btn">{buttons}</div>'

def form_service_gen_multiple_values(id, params, service):
	values = []
	for env in service:
		if env.startswith(params[0]["env"]):
			suffix = env.replace(params[0]["env"], "")
			for param in params:
				value = {
					"id": param["id"],
					"env": param["env"],
					"label": param["label"],
					"type": param["type"],
					"default": service[param["env"] + suffix]
					if param["env"] + suffix in service
					else param["default"],
				}
				values.append(value)
	return f"addMultiple('{id}', '{json.dumps(values)}'); " if values else ""
