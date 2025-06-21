from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# DB Initialization---------------------------
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    #User table for login
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin')")

    #table for stored XSS comment
    cursor.execute("CREATE TABLE IF NOT EXISTS comments (name TEXT, message TEXT)")

    conn.commit()
    conn.close()

init_db()

#Login Route(SQLi)---------------------------------
@app.route('/', methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        #SQL Injection vuln code
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()

        if result:
            return redirect("/admin")
        else:
            return "Invalid Credentials"
    
    return render_template("login.html")


#Admin Route------------------------------------
@app.route('/admin')
def admin():
    return render_template("admin.html")


#File Upload Route(Command Injection)-------
@app.route("/upload", methods=["GET","POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        #Command Injection Vuln
        os.system(f"unzip {filepath} -d {UPLOAD_FOLDER}")

        return "File uploaded and extracted!"
    return render_template("upload.html")


#Reflected XSS Route---------------------------------
@app.route('/search')
def search():
    query = request.args.get("q","")
    return render_template('search.html', query=query)

#Stored XSS Route--------------------------
@app.route('/comment', methods=["GET","POST"])
def comment():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        message = request.form["message"]
        cursor.execute("INSERT INTO comments (name, message) VALUES (?, ?)", (name, message))
        conn.commit()

    cursor.execute("SELECT name, message FROM comments") 
    comments = cursor.fetchall()
    conn.close()

    return render_template("comment.html", comments=comments)

#App Runner-------------------------------
if __name__ == "__main__":
    app.run(debug=True)