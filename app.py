import pandas as pd
import numpy as np

from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "ems_secret_key"


# ---------------- DATABASE ---------------- #

def get_connection():
    conn = sqlite3.connect("employee.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # Admin Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Employee Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        department TEXT,
        designation TEXT,
        salary REAL,
        gender TEXT,
        address TEXT,
        joining_date TEXT
    )
    """)

    # Default Admin
    cur.execute("SELECT * FROM admin")

    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO admin(username,password) VALUES(?,?)",
            ("admin", "admin123")
        )

    conn.commit()
    conn.close()


create_tables()


# ---------------- LOGIN ---------------- #

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        )

        admin = cur.fetchone()
        conn.close()

        if admin:
            session["admin"] = username
            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid Username or Password"
        )

    return render_template("login.html")


# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    # Total Employees
    cur.execute("SELECT COUNT(*) FROM employees")
    total_employees = cur.fetchone()[0]

    # Total Departments
    cur.execute("SELECT COUNT(DISTINCT department) FROM employees")
    total_departments = cur.fetchone()[0]

    # Total Payroll
    cur.execute("SELECT IFNULL(SUM(salary),0) FROM employees")
    total_salary = cur.fetchone()[0]

    # Average Salary
    cur.execute("SELECT IFNULL(AVG(salary),0) FROM employees")
    average_salary = round(cur.fetchone()[0], 2)

    conn.close()

    return render_template(
        "dashboard.html",
        total_employees=total_employees,
        total_departments=total_departments,
        total_salary=total_salary,
        average_salary=average_salary
    )
# ---------------- ADD EMPLOYEE ---------------- #

@app.route("/add")
def add_employee():

    if "admin" not in session:
        return redirect(url_for("login"))

    return render_template("add_employee.html")


# ---------------- SAVE EMPLOYEE ---------------- #

@app.route("/save_employee", methods=["POST"])
def save_employee():

    if "admin" not in session:
        return redirect(url_for("login"))

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    department = request.form["department"]
    designation = request.form["designation"]
    salary = request.form["salary"]
    gender = request.form["gender"]
    address = request.form["address"]
    joining_date = request.form["joining_date"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO employees
        (name,email,phone,department,designation,salary,gender,address,joining_date)
        VALUES(?,?,?,?,?,?,?,?,?)
    """, (
        name,
        email,
        phone,
        department,
        designation,
        salary,
        gender,
        address,
        joining_date
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("view_employees"))


# ---------------- VIEW EMPLOYEES ---------------- #

@app.route("/employees")
def view_employees():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM employees ORDER BY id DESC")
    employees = cur.fetchall()

    conn.close()

    return render_template(
        "view_employee.html",
        employees=employees
    )
# ---------------- SEARCH EMPLOYEE ---------------- #

@app.route("/search", methods=["GET"])
def search_employee():

    if "admin" not in session:
        return redirect(url_for("login"))

    keyword = request.args.get("keyword", "").strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM employees
        WHERE
            name LIKE ?
            OR email LIKE ?
            OR department LIKE ?
            OR designation LIKE ?
    """, (
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    employees = cur.fetchall()

    conn.close()

    return render_template(
        "view_employee.html",
        employees=employees
    )


# ---------------- EDIT EMPLOYEE ---------------- #

@app.route("/edit/<int:id>")
def edit_employee(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM employees WHERE id=?", (id,))
    employee = cur.fetchone()

    conn.close()

    return render_template(
        "edit_employee.html",
        employee=employee
    )


# ---------------- UPDATE EMPLOYEE ---------------- #

@app.route("/update_employee/<int:id>", methods=["POST"])
def update_employee(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    department = request.form["department"]
    designation = request.form["designation"]
    salary = request.form["salary"]
    gender = request.form["gender"]
    address = request.form["address"]
    joining_date = request.form["joining_date"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE employees
        SET
            name=?,
            email=?,
            phone=?,
            department=?,
            designation=?,
            salary=?,
            gender=?,
            address=?,
            joining_date=?
        WHERE id=?
    """, (
        name,
        email,
        phone,
        department,
        designation,
        salary,
        gender,
        address,
        joining_date,
        id
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("view_employees"))
# ---------------- DELETE EMPLOYEE ---------------- #

@app.route("/delete/<int:id>")
def delete_employee(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM employees WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("view_employees"))
@app.route("/reports")
def reports():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = get_connection()

    df = pd.read_sql_query("SELECT * FROM employees", conn)

    conn.close()

    if len(df) == 0:

        return render_template(
            "reports.html",
            total=0,
            average=0,
            maximum=0,
            minimum=0
        )

    salaries = df["salary"].astype(float).to_numpy()

    total = len(df)
    average = np.mean(salaries)
    maximum = np.max(salaries)
    minimum = np.min(salaries)

    return render_template(
        "reports.html",
        total=total,
        average=round(average,2),
        maximum=maximum,
        minimum=minimum
    )


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------- RUN APPLICATION ---------------- #

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)