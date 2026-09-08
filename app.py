from flask import Flask, render_template, redirect, session, request
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


def get_db():
    db = sqlite3.connect("emails.db")
    db.row_factory = sqlite3.Row
    return db

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def mainDir():
    if "user_id" in session:
        return redirect("/inbox")
    return redirect("/login")


@app.route("/sent")
def sent():
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    emails = db.execute("""
        SELECT
            emails.email_id,
            users.username AS recipient,
            users.display_name AS recipient_name,
            emails.time_sent,
            emails.title,
            emails.description
        FROM emails
        JOIN users
            ON emails.recipient_id = users.user_id
        WHERE emails.sender_id = ?
        ORDER BY emails.time_sent DESC
    """, (session["user_id"],)).fetchall()

    db.close()

    return render_template("sent.html", emails=emails)


@app.route("/inbox")
def inbox():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    query = request.args.get("q", "")

    db = get_db()

    if query:
        emails = db.execute("""
            SELECT
                emails.email_id,
                users.username AS sender,
                users.display_name AS sender_name,
                emails.time_sent,
                emails.title,
                emails.description,
                emails.is_read
            FROM emails
            JOIN users
                ON emails.sender_id = users.user_id
            WHERE emails.recipient_id = ?
              AND (
                  users.username LIKE ?
                  OR emails.title LIKE ?
                  OR emails.description LIKE ?
              )
            ORDER BY emails.time_sent DESC
        """, (
            user_id,
            "%" + query + "%",
            "%" + query + "%",
            "%" + query + "%"
        )).fetchall()

    else:
        emails = db.execute("""
            SELECT
                emails.email_id,
                users.username AS sender,
                users.display_name AS sender_name,
                emails.time_sent,
                emails.title,
                emails.description,
                emails.is_read
            FROM emails
            JOIN users
                ON emails.sender_id = users.user_id
            WHERE emails.recipient_id = ?
            ORDER BY emails.time_sent DESC
        """, (user_id,)).fetchall()

    count = db.execute("""
        SELECT COUNT(*) AS count
        FROM emails
        WHERE recipient_id = ?
        AND is_read = 0;
    """, (user_id,)).fetchone()

    db.close()

    return render_template(
        "inbox.html",
        emails=emails,
        query=query,
        inbox_count=count
    )

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    db = get_db()

    user = db.execute("""
        SELECT user_id, password_hash
        FROM users
        WHERE username = ?
    """, (username,)).fetchone()

    db.close()

    if user is None or not check_password_hash(
        user["password_hash"],
        password #type:ignore #don't worry, we can ignore this, the problem comes because vs code password can be None but in the html form we forced it to be required 
    ):
        return render_template(
            "login.html",
            message="Username or password is incorrect"
        )

    session["user_id"] = user["user_id"]

    return redirect("/inbox")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", message="")

    username = request.form.get("username")
    displayname = request.form.get("display_name")
    password = request.form.get("password")

    db = get_db()

    user = db.execute("""
        SELECT user_id
        FROM users
        WHERE username = ?
    """, (username,)).fetchone()

    if user is not None:
        db.close()
        return render_template(
            "register.html",
            message="Username already exists."
        )

    password_hash = generate_password_hash(password) #type: ignore #don't worry, we can ignore this, the problem comes because vs code password can be None but in the html form we forced it to be required 

    cursor = db.execute("""
        INSERT INTO users (username, display_name, password_hash)
        VALUES (?, ?, ?)
    """, (username, displayname, password_hash))

    db.commit()

    user_id = cursor.lastrowid

    db.close()

    session["user_id"] = user_id

    return redirect("/inbox")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/email/<int:email_id>")
def email(email_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    email = db.execute("""
        SELECT
            emails.email_id,
            sender.username AS sender,
            sender.display_name AS sender_name,
            receiver.username AS recipient,
            receiver.display_name AS recipient_name,
            emails.time_sent,
            emails.title,
            emails.description,
            emails.is_read
        FROM emails
        JOIN users AS sender
            ON emails.sender_id = sender.user_id
        JOIN users AS receiver
            ON emails.recipient_id = receiver.user_id
        WHERE emails.email_id = ?
          AND (
              emails.sender_id = ?
              OR emails.recipient_id = ?
          )
    """, (
        email_id,
        session["user_id"],
        session["user_id"]
    )).fetchone()

    if email is None:
        db.close()
        return "Email not found", 404

    db.execute("""
        UPDATE emails
        SET is_read = 1
        WHERE email_id = ?
          AND recipient_id = ?
    """, (email_id, session["user_id"]))

    db.commit()
    db.close()

    return render_template("email.html", email=email)


@app.route("/compose", methods=["GET", "POST"])
def compose():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "GET":
        return render_template("compose.html")

    recipient = request.form.get("recipient")
    title = request.form.get("title")
    description = request.form.get("description")

    db = get_db()

    user = db.execute("""
        SELECT user_id
        FROM users
        WHERE username = ?
    """, (recipient,)).fetchone()

    if user is None:
        db.close()
        return "Recipient does not exist", 404

    db.execute("""
        INSERT INTO emails
        (sender_id, recipient_id, time_sent, title, description)
        VALUES (?, ?, datetime('now'), ?, ?)
    """, (
        session["user_id"],
        user["user_id"],
        title,
        description
    ))

    db.commit()
    db.close()

    return redirect("/inbox")

@app.route("/delete/<int:email_id>", methods=["POST"])
def delete(email_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    db.execute("""
        DELETE FROM emails
        WHERE email_id = ?
        AND recipient_id = ?
    """, (email_id, session["user_id"]))

    db.commit()
    db.close()

    return redirect("/inbox")

@app.route("/reply/<int:email_id>", methods = ["GET", "POST"])
def reply(email_id):

    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    email = db.execute("""
        SELECT
            emails.email_id,
            emails.sender_id,
            emails.recipient_id,
            emails.title,
            sender.username AS sender,
            receiver.username AS recipient
        FROM emails
        JOIN users AS sender
            ON emails.sender_id = sender.user_id
        JOIN users AS receiver
            ON emails.recipient_id = receiver.user_id
        WHERE emails.email_id = ?
          AND (
              emails.sender_id = ?
              OR emails.recipient_id = ?
          )
    """, (
        email_id,
        session["user_id"],
        session["user_id"]
    )).fetchone()

    db.close()

    if email is None:
        return "Email not found", 404

    if email["recipient_id"] == session["user_id"]:
        recipient = email["sender"]
    else:
        recipient = email["recipient"]

    return render_template(
        "compose.html",
        recipient=recipient,
        title="Re: " + email["title"]
    )


if __name__ == "__main__":
    app.run()