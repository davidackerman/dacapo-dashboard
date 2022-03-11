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
from werkzeug.security import check_password_hash, generate_password_hash

from dashboard.stores import get_stores

from bson.objectid import ObjectId

bp = Blueprint("auth", __name__, url_prefix="/auth")

# TODO: Where to put users now
@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_stores()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."
        elif db.users.find_one({"username": username}) is not None:
            error = "Username already exists."

        if error is None:
            db.users.insert_one(
                {"username": username, "password": generate_password_hash(password)}
            )
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_stores()
        error = None
        user = db.users.find_one({"username": username})

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = str(user["_id"])
            return redirect(url_for("dacapo.get_results"))

        flash(error)

    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_stores().users.find_one({"_id": ObjectId(user_id)})


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
