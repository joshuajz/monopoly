# app.py
# TODO: Create a "home" page to display what the website does
# TODO: Create a readme
# TODO: Write a bunch of comments, clean up file system, remove not neeeded functions (Esp. from monopoly)
# TODO: Clear database for final upload of files
# TODO: CLear all extra todos from other files

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, g, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from monopoly import run_rolls
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


@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def index():
    return render_template("home.html")


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
        return redirect("/simulate")


@app.route("/simulate", methods=["GET", "POST"])
@login_required
def simulate():
    if request.method == "GET":
        return render_template("simulate.html")
    else:
        amount = int(request.form.get("amount"))
        if 0 >= amount or amount >= 1000000:
            return error("422: Invalid Roll Amount", "/simulate")
        roll_session = run_rolls(amount)

        print(session["id"])

        db.execute(
            "INSERT INTO user_sessions (user_id, session_id) VALUES (:id, :session)",
            id=session["id"],
            session=roll_session,
        )

        return redirect("/dashboard")


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    def dash(current_id="NULL"):
        ids = db.execute(
            "SELECT session_id FROM user_sessions WHERE user_id = :id", id=session["id"]
        )

        if current_id == "NULL":
            current_id = ids[0]["session_id"]

        stats = db.execute("SELECT * FROM stats WHERE session_id=:id", id=current_id)[0]
        landed = db.execute("SELECT * FROM landed WHERE session_id=:id", id=current_id)[
            0
        ]
        landed.pop("session_id")
        l = tuple(landed.values())

        graph(l, 17)

        # landed needs to be a list/dictionary w/
        # location name (w/ a colur)
        # landed amount
        # landed percentage

        board_info = db.execute("SELECT name FROM board")

        final_landed = []

        colours = [
            "black",
            "brown",
            "grey",
            "brown",
            "grey",
            "#03b6fc",
            "blue",
            "grey",
            "blue",
            "blue",
            "black",
            "purple",
            "grey",
            "purple",
            "purple",
            "#03b6fc",
            "orange",
            "grey",
            "orange",
            "orange",
            "black",
            "red",
            "grey",
            "red",
            "red",
            "#03b6fc",
            "#cfc50a",
            "#cfc50a",
            "grey",
            "#cfc50a",
            "black",
            "green",
            "green",
            "grey",
            "green",
            "#03b6fc",
            "grey",
            "darkblue",
            "darkblack",
            "darkblue",
        ]

        amount_landed = sum(landed.values())

        for value in landed.values():
            final_landed.append(
                {
                    "name": board_info.pop(0)["name"],
                    "colour": colours.pop(0),
                    "landed_amount": value,
                    "landed_percentage": value / amount_landed * 100,
                }
            )

        for location in final_landed:
            print(location)

        return render_template(
            "dashboard.html", ids=ids, stat=stats, landed=final_landed
        )

    if request.method == "POST":
        return dash(request.form.get("ids"))
    else:
        return dash()
