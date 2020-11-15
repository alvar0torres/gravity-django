import os
import sqlalchemy
import flask_sqlalchemy

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import inspect
from flask_sqlalchemy import SQLAlchemy


from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("postgres://ziznnimeremyjy:3d1b6b35cb8015c5a0b0f4e77b82234578ae4ffba7ee4524d1ed96bd5fc13ce5@ec2-54-217-224-85.eu-west-1.compute.amazonaws.com:5432/d9dbadah2gk8f7")



@app.route("/")
@login_required
def index():

    return render_template("welcome.html")


@app.route("/history")
@login_required
def history():
    """Show history of calculations"""
    history = db.execute("SELECT * FROM history WHERE id=:id", id=session["user_id"])
    print(history)
    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return render_template("calculator.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/calculator", methods=["GET", "POST"])
@login_required
def calculator():
    """Enter data for doing the calculations."""

    if request.method == "GET":
        return render_template("calculator.html")

    if request.method == "POST":

        if not request.form.get("planet"):
            return apology("You must choose a world")
        if not request.form.get("weight"):
            return apology("You must enter weight")
        else:

            moon = 1.622

            mercury = 3.70

            venus = 8.87

            mars = 3.71

            jupiter = 24.79

            saturn = 10.44

            uranus = 8.69

            neptune = 11.00

            pluto = 0.62

            choice = request.form.get("planet")

            if choice == "Moon":
                choice = moon
            elif choice == "Mercury":
                choice = mercury
            elif choice == "Venus":
                choice = venus
            elif choice == "Mars":
                choice = mars
            elif choice == "Jupiter":
                choice = jupiter
            elif choice == "Saturn":
                choice = saturn
            elif choice == "Uranus":
                choice = uranus
            elif choice == "Neptune":
                choice = neptune
            elif choice == "Pluto":
                choice = pluto

            entered_weight = request.form.get("weight")

            result = int(entered_weight)*choice/9.8
            result = round(result, 2)

            choice = request.form.get("planet")

            db.execute("INSERT INTO history (id, world, earth_weight, world_weight, date) VALUES (:id, :world, :earth_weight, :world_weight, :date)", id=session["user_id"], world=choice, earth_weight=entered_weight, world_weight=result, date=datetime.now().strftime("%Y-%m-%d"))
            return render_template("result.html", moon=moon, mercury=mercury, venus=venus, mars=mars, jupiter=jupiter, saturn=saturn, uranus=uranus, neptune=neptune, choice=choice, entered_weight=entered_weight, result=result, pluto=pluto)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
         # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure email was submitted
        elif not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 403)

        # Ensure password and confirmation match:
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation do not match", 403)

        # Querying the database
        users = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Hashing password
        hashed = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        # Puting username and email into variables:
        username = request.form.get("username")
        email = request.form.get("email")

        counter=0

        # Making sure user enters @
        for i in email:
            if i == "@":
                counter += 1

        if counter != 1:
                return apology("Please enter a valid email")

        # Checking if the user exists and inserting if negative
        if len(users) != 1:
            db.execute("INSERT INTO users (username, hash, email) VALUES (:username, :hashed, :email)", username=username, hashed=hashed, email=email)
            return redirect("/")
        else:
            return apology("That username already exists")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
