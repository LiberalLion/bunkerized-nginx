#!/usr/bin/python3

from flask import Flask, render_template, current_app, request, redirect
from flask_login import LoginManager, login_required, login_user, logout_user
from flask_wtf.csrf import CSRFProtect, CSRFError

from src.Instances import Instances
from src.User import User
from src.Config import Config
from src.ReverseProxied import ReverseProxied

import utils
import os, json, re, copy, traceback

# Flask app
app = Flask(__name__, static_url_path="/", static_folder="static", template_folder="templates")
app.wsgi_app = ReverseProxied(app.wsgi_app)

# Set variables and instantiate objects
vars = utils.get_variables()
app.secret_key = vars["FLASK_SECRET"]
app.config["ABSOLUTE_URI"] = vars["ABSOLUTE_URI"]
app.config["INSTANCES"] = Instances(vars["DOCKER_HOST"], vars["API_URI"])
app.config["CONFIG"] = Config()
app.config["SESSION_COOKIE_DOMAIN"] = vars["ABSOLUTE_URI"].replace("http://", "").replace("https://", "").split("/")[0]
app.config["WTF_CSRF_SSL_STRICT"] = False

# Declare functions for jinja2
app.jinja_env.globals.update(env_to_summary_class=utils.env_to_summary_class)
app.jinja_env.globals.update(form_service_gen=utils.form_service_gen)
app.jinja_env.globals.update(form_service_gen_multiple=utils.form_service_gen_multiple)
app.jinja_env.globals.update(form_service_gen_multiple_values=utils.form_service_gen_multiple_values)

#@app.before_request
#def log_request():
#    app.logger.debug("Request Headers %s", request.headers)
#    return None

# Login management
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
user = User(vars["ADMIN_USERNAME"], vars["ADMIN_PASSWORD"])
app.config["USER"] = user
@login_manager.user_loader
def load_user(user_id):
    return User(user_id, vars["ADMIN_PASSWORD"])

# CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
	return render_template("error.html", title="Error", error="Wrong CSRF token !"), 401

@app.route('/login', methods=["GET", "POST"])
def login() :
	fail = False
	if request.method == "POST" and "username" in request.form and "password" in request.form :
		if app.config["USER"].get_id() == request.form["username"] and app.config["USER"].check_password(request.form["password"]) :
			login_user(app.config["USER"])
			return redirect(app.config["ABSOLUTE_URI"])
		else :
			fail = True
	if fail :
		return render_template("login.html", title="Login", fail=True), 401
	return render_template("login.html", title="Login", fail=False)

@app.route("/logout")
@login_required
def logout() :
    logout_user()
    return redirect(app.config["ABSOLUTE_URI"] + "/login")

@app.route('/')
@app.route('/home')
@login_required
def home():
    try:
        instances_number = len(app.config["INSTANCES"].get_instances())
        services_number = len(app.config["CONFIG"].get_services())
        return render_template("home.html", title="Home", instances_number=instances_number, services_number=services_number)
    except Exception as e:
        return render_template(
            "error.html",
            title="Error",
            error=f"{str(e)}<br />"
            + traceback.format_exc().replace("\n", "<br />"),
        )

@app.route('/instances', methods=["GET", "POST"])
@login_required
def instances():
    try:
        # Manage instances
        operation = ""
        if request.method == "POST":

            			# Check operation
            if "operation" not in request.form or request.form[
                "operation"
            ] not in ["reload", "start", "stop", "restart"]:
                raise Exception("Missing operation parameter on /instances.")

            			# Check that all fields are present
            if "INSTANCE_ID" not in request.form:
                raise Exception("Missing INSTANCE_ID parameter.")

            # Do the operation
            if request.form["operation"] == "reload" :
            	operation = app.config["INSTANCES"].reload_instance(request.form["INSTANCE_ID"])
            elif request.form["operation"] == "start" :
            	operation = app.config["INSTANCES"].start_instance(request.form["INSTANCE_ID"])
            elif request.form["operation"] == "stop" :
            	operation = app.config["INSTANCES"].stop_instance(request.form["INSTANCE_ID"])
            elif request.form["operation"] == "restart" :
            	operation = app.config["INSTANCES"].restart_instance(request.form["INSTANCE_ID"])

        # Display instances
        instances = app.config["INSTANCES"].get_instances()
        return render_template("instances.html", title="Instances", instances=instances, operation=operation)

    except Exception as e :
    	return render_template("error.html", title="Error", error=str(e) + "\n" + traceback.format_exc())


@app.route('/services', methods=["GET", "POST"])
@login_required
def services():
    try:
        # Manage services
        operation = ""
        if request.method == "POST":

            			# Check operation
            if "operation" not in request.form or request.form[
                "operation"
            ] not in ["new", "edit", "delete"]:
                raise Exception("Missing operation parameter on /services.")

            # Check variables
            variables = copy.deepcopy(request.form.to_dict())
            del variables["csrf_token"]
            if (
                "OLD_SERVER_NAME" not in request.form
                and request.form["operation"] == "edit"
            ):
                raise Exception("Missing OLD_SERVER_NAME parameter.")
            if request.form["operation"] in ["new", "edit"]:
                del variables["operation"]
                if request.form["operation"] == "edit" :
                	del variables["OLD_SERVER_NAME"]
                app.config["CONFIG"].check_variables(variables)

            elif request.form["operation"] == "delete":
                if "SERVER_NAME" not in request.form:
                    raise Exception("Missing SERVER_NAME parameter.")
                app.config["CONFIG"].check_variables({"SERVER_NAME" : request.form["SERVER_NAME"]})

            # Do the operation
            if request.form["operation"] == "new" :
            	operation = app.config["CONFIG"].new_service(variables)
            elif request.form["operation"] == "edit" :
            	operation = app.config["CONFIG"].edit_service(request.form["OLD_SERVER_NAME"], variables)
            elif request.form["operation"] == "delete" :
            	operation = app.config["CONFIG"].delete_service(request.form["SERVER_NAME"])

            # Reload instances
            reload = app.config["INSTANCES"].reload_instances()
            if not reload :
            	operation = "Reload failed for at least one instance..."

        # Display services
        services = app.config["CONFIG"].get_services()
        return render_template("services.html", title="Services", services=services, operation=operation)

    except Exception as e :
    	return render_template("error.html", title="Error", error=str(e) + "\n" + traceback.format_exc())
