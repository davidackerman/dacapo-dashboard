import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_manager
import flask_login
from flask_login.utils import login_required
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms.fields.simple import TextAreaField
from dashboard.authservice import create_auth_service

from dashboard.stores import get_stores

from bson.objectid import ObjectId


from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, PasswordField

from dashboard.nextflow import Nextflow

bp = Blueprint("auth", __name__, url_prefix="/auth")


class LoginForm(FlaskForm):
    username = StringField(
        "username", validators=[DataRequired("Username is required")]
    )
    password = PasswordField(
        "password", validators=[DataRequired("Password is required")]
    )


class RegisterForm(FlaskForm):
    username = StringField(
        "username", validators=[DataRequired("Username is required")]
    )
    password = PasswordField(
        "password", validators=[DataRequired("Password is required")]
    )
    api_token = StringField(
        "api_token", validators=[DataRequired("API token is required")],
    )
    ssh_key = TextAreaField("ssh_key", validators=[DataRequired("SSH key is required")])


# TODO: Where to put users now


@bp.route("/register_form", methods=["GET", "POST"])
def register_form():
    next_page = request.args.get("next")
    print("register_form", next_page)
    form = RegisterForm(csrf_enabled=True)
    if not form.validate_on_submit():
        return render_template("auth/register.html", form=form, next=next_page), 401
    return render_template(
        "auth/register.html", form=form, next=next_page if next_page else ""
    )


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.args.get("next"):
        next_page = request.args.get("next")
    elif request.form.get("next"):
        next_page = request.form.get("next")
    else:
        next_page = url_for("main")

    form = RegisterForm(csrf_enabled=True)
    auth_service = create_auth_service()
    username = form.username.data
    user_credentials = {"username": username, "password": form.password.data}
    api_token = form.api_token.data
    ssh_key = form.ssh_key.data
    authResponse = auth_service.authenticate_user(user_credentials)
    error_message = ""
    if authResponse.status_code == 200:
        user_info = {"name": username, "api_token": api_token}
        nextflow = Nextflow(user_info, ssh_key)
        if nextflow.verified:
            config_store = get_stores().config
            config_store.store_user_info(user_info)
            auth_service.login(user_credentials)
            session["user_info"] = user_info
            # setup_compute_environment...
            return redirect(next_page)
        else:
            error_message = nextflow.error_message
    else:
        error_message = "Invalid Username or Password"

    return render_template(
        "auth/register.html", form=form, next=next_page, error_message=error_message
    )


@bp.route("/login_form", methods=["GET", "POST"])
def login_form():
    next_page_param = request.args.get("next")
    form = LoginForm(csrf_enabled=True)
    if not form.validate_on_submit():
        form = LoginForm(csrf_enabled=True)
        return render_template("auth/login.html", form=form, next=next_page_param), 401
    return render_template(
        "auth/login.html", form=form, next=next_page_param if next_page_param else ""
    )


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.args.get("next"):
        next_page = request.args.get("next")
    elif request.form.get("next"):
        next_page = request.form.get("next")
    else:
        next_page = url_for("main")

    if not next_page:
        next_page = ""

    form = LoginForm(csrf_enabled=True)
    # if not form.validate_on_submit():
    #     form = LoginForm(csrf_enabled=True)
    #     return render_template('auth/login.html',
    #                            form=form,
    #                            next=next), 401

    # execute login
    auth_service = create_auth_service()
    user_credentials = {"username": form.username.data, "password": form.password.data}
    authResponse = auth_service.authenticate_user(user_credentials)

    if authResponse.status_code == 200:
        config_store = get_stores().config
        user_info = config_store.retrieve_user_info(user_credentials["username"])
        if user_info:
            logged_in = auth_service.login(user_credentials)
            session["user_info"] = user_info
            if logged_in:
                return redirect(next_page)
        else:
            return redirect(url_for("auth.register_form", next=next_page))
    else:
        return (
            render_template(
                "auth/login.html",
                form=form,
                next=next_page,
                error_message="Invalid Username or Password",
            ),
            401,
        )


@bp.before_app_request
def load_logged_in_user():
    if hasattr(flask_login.current_user, "username"):
        config_store = get_stores().config
        user_info = config_store.retrieve_user_info(flask_login.current_user.username)
        g.user_info = user_info


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main"))
