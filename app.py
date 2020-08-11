# app.py
# TODO: Register should redirect to login page
# TODO: Login page
# TODO: Sessions

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, g, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from graphing import graph


app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

db = SQL("sqlite:///database.db")

# Secret_key
app.secret_key = '''b"\xcc\xe7h\xa26pv\x98qmR_\x96K\xe5.\x98\xcd\xa7\xed\xb4D'\xd1\x1f\x15\x01f\xd1\xaa\x16c\xb9\xb8f\xc4"'''

# Source: https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session["username"] is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    return render_template("layout.html", session=session)


@app.route("/error")
def error(message, back):
    return render_template("error.html", message=message, back=back)


# Add a banner for a successful registration that automaticlly disappears
# https://stackoverflow.com/questions/23101966/bootstrap-alert-auto-close
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        user = request.form.get("username")
        if not user:
            return error("422: Invalid Username Input", "/register")
        password = request.form.get("password")
        if not password:
            return error("422: Invalid Password Input", "/register")
        confirmation = request.form.get("confirmation")
        if not confirmation:
            return error("422: Invalid Confirmation Input", "/register")
        if password != confirmation:
            return error("422: Password does not Equal Confirmation", "register")

        taken = db.execute(
            "SELECT COUNT(username) FROM users WHERE username=:username", username=user
        )[0]["COUNT(username)"]
        if taken != 0:
            return error("422: Username Already Taken", "/register")

        hashed_password = generate_password_hash(password)

        db.execute(
            "INSERT INTO users (username, password) VALUES (:username, :password)",
            username=user,
            password=hashed_password,
        )

        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        user = request.form.get("username")
        if not user:
            return error("422: Invalid Username", "/login")

        password = request.form.get("password")
        if not password:
            return error("422: Invalid Password", "/login")

        # Does the user exist in the database?
        if (
            db.execute(
                "SELECT COUNT(1) FROM users WHERE username=:username", username=user
            )[0]["COUNT(1)"]
            == 0
        ):
            return error("422: Invalid Username", "/login")

        # Pulls the user information
        user = db.execute(
            "SELECT * FROM users WHERE username=:username", username=user
        )[0]

        if not check_password_hash(user["password"], password):
            return error("422: Invalid Password", "/login")

        session["username"] = user["username"]
        session["id"] = user["user_id"]
        print("DEBUG:Successful Login")
        return redirect("/dashboard")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        print("Submitted form")
    else:
        ids = db.execute("SELECT session_id FROM user_sessions WHERE user_id = 0")
        current_id = 17
        stats = db.execute("SELECT * FROM stats WHERE session_id=:id", id=current_id)[0]
        landed = db.execute("SELECT * FROM landed WHERE session_id=17")[0]
        landed.pop("session_id")
        l = tuple(landed.values())
        print(l)
        graph(l, 17)
        return render_template("dashboard.html", ids=ids, stat=stats)
