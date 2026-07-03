from flask import Flask, render_template, request, redirect, send_file
import sqlite3
from openpyxl import Workbook
from datetime import datetime

app = Flask(__name__)

# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect("expenses.db")
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            item TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT
        )
    """)

    conn.commit()
    return conn


# ---------------- HOME ----------------

@app.route("/", methods=["GET", "POST"])
def index():

    db = get_db()

    if request.method == "POST":

        user = request.form["user"]
        item = request.form["item"]
        amount = float(request.form["amount"])

        current_date = datetime.now().strftime("%d-%m-%Y %I:%M %p")

        db.execute(
            """
            INSERT INTO expenses(user,item,amount,date)
            VALUES(?,?,?,?)
            """,
            (user, item, amount, current_date)
        )

        db.commit()

        return redirect("/")

    expenses = db.execute(
        "SELECT * FROM expenses ORDER BY id DESC"
    ).fetchall()

    total = sum(expense["amount"] for expense in expenses)

    per_person = total / 4 if total > 0 else 0

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        per_person=per_person
    )


# ---------------- DELETE ----------------

# ---------------- DELETE ----------------

@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):

    if request.method == "POST":

        password = request.form["password"]

        # Yahan apna password change kar sakte ho
        if password == "admin123":

            db = get_db()
            db.execute("DELETE FROM expenses WHERE id=?", (id,))
            db.commit()

            return redirect("/")

        else:
            flash("Wrong Password!")

    return render_template("delete.html", id=id)

# ---------------- EXPORT EXCEL ----------------

@app.route("/export")
def export():

    db = get_db()

    expenses = db.execute(
        "SELECT * FROM expenses"
    ).fetchall()

    wb = Workbook()

    ws = wb.active

    ws.title = "Room Expenses"

    ws.append([
        "ID",
        "User",
        "Item",
        "Amount",
        "Date"
    ])

    for expense in expenses:

        ws.append([
            expense["id"],
            expense["user"],
            expense["item"],
            expense["amount"],
            expense["date"]
        ])

    filename = "expenses.xlsx"

    wb.save(filename)

    return send_file(
        filename,
        as_attachment=True
    )


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)

# ---------------- DELETE ----------------

@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete(id):

    if request.method == "POST":

        password = request.form["password"]

        # Admin Password
        if password == "admin123":

            db = get_db()

            db.execute(
                "DELETE FROM expenses WHERE id=?",
                (id,)
            )

            db.commit()

            # Excel automatically update after delete
            update_excel()

            flash("Expense Deleted Successfully!", "success")

            return redirect("/")

        else:

            flash("❌ Wrong Password!", "error")

    return render_template("delete.html", id=id)


# ---------------- EXPORT EXCEL ----------------

@app.route("/export")
def export():

    # Make sure Excel is always up-to-date
    update_excel()

    return send_file(
        "expenses.xlsx",
        as_attachment=True,
        download_name="Room_Expenses.xlsx"
    )


# ---------------- RESET ALL DATA ----------------

@app.route("/reset", methods=["POST"])
def reset():

    password = request.form["password"]

    if password == "admin123":

        db = get_db()

        db.execute("DELETE FROM expenses")

        db.commit()

        # Empty Excel File
        update_excel()

        flash("All Expenses Deleted Successfully!", "success")

    else:

        flash("Wrong Password!", "error")

    return redirect("/")


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)