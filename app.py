from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, os, hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

DB_NAME = "users.db"


def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            """CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)"""
        )
        conn.commit()
        conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])
        try:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
            conn.commit()
            conn.close()
            flash("註冊成功，請登入！")
            return render_template("index.html")
        except sqlite3.IntegrityError:
            flash("使用者名稱已存在")
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = hash_password(request.form["password"])

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        )
        user = c.fetchone()
        conn.close()

        if user:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("帳號或密碼錯誤")
            return redirect(url_for("home"))  # 導回首頁，再顯示錯誤訊息

    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return render_template("index.html")
    return render_template("dashboard.html", username=session["username"])


@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("已登出")
    return render_template("index.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
