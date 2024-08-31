import os

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from cs50 import SQL
from datetime import date
import secrets

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = secrets.token_hex(32)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///events.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        school = request.form.get("school")
        schools = db.execute("SELECT * FROM schools")
        schools_list = [value for dct in schools for value in dct.values()]
        if school not in schools_list:
            return render_template("index.html", schools=schools, message="Please add school before searching")
        session["school"] = school 
        events = db.execute("SELECT * FROM events WHERE date >= ? AND school = ? ORDER BY date ASC, time ASC", date.today(), session.get("school"))
        return render_template("results.html", school=school, events=events)
    else:
        session["school"] = None
        schools = db.execute("SELECT * FROM schools ORDER BY school")
        return render_template("index.html", schools=schools)
    
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        school = request.form.get("school")
        if school != "":
            try:
                db.execute("INSERT INTO schools VALUES (?)", school)
            except ValueError:
                return redirect("/")
        return redirect("/")
    else:
        return render_template("add.html")
    
@app.route("/add_event", methods=["GET", "POST"])
def add_event():
    if request.method == "POST":
        if session.get("school"):
            name = request.form.get("name")
            location = request.form.get("location")
            info = request.form.get("info")
            month = request.form.get("month")
            day = request.form.get("day")
            year = request.form.get("year")
            hour = request.form.get("hour")
            minute = request.form.get("minute")
            am_pm = request.form.get("am/pm")
            event_date = year + '-' + month + '-' + day
            if am_pm == "p.m":
                if hour == '12':
                    time = hour + '-' + minute + '-' + '00'
                else:
                    time = str(12 + int(hour)) + '-' + minute + '-' + '00'
            elif hour == '12':
                time = '00' + '-' + minute + '-' + '00'
            else:
                time = hour + '-' + minute + '-' + '00'
            digital_time = hour + ':' + minute + ' ' + am_pm
            db.execute("INSERT INTO events (school, name, location, info, date, time, digital_time) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        session.get("school"), name, location, info, event_date, time, digital_time)
            events = db.execute("SELECT * FROM events WHERE date >= ? AND school = ? ORDER BY date ASC, time ASC", date.today(), session.get("school"))
            return render_template("results.html", school=session.get("school"), events=events)
        else:
            return redirect("/")
    elif session.get("school"):
        return render_template("add_event.html", school=session.get("school"))
    else:
        return redirect("/")
    
@app.route("/results")
def results():
    school = session.get("school")
    if not school:
        return redirect("/")
    events = db.execute("SELECT * FROM events WHERE date >= ? AND school = ? ORDER BY date ASC, time ASC", date.today(), session.get("school"))
    return render_template("results.html", school=school, events=events)