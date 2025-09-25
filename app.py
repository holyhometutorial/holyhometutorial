from flask import Flask, render_template, request, jsonify, send_file
import sqlite3, os, csv, io
from datetime import datetime

app = Flask(__name__)

DB_PATH = 'holyhome.db'

# डेटाबेस टेबल बनाना
def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS registrations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fname TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            class_applying TEXT NOT NULL,
            guardian TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    con.close()

@app.route('/')
def form():
    return render_template('reg.html')

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    required = ['fname','dob','gender','class','guardian','phone','address']
    if not all(data.get(k) for k in required):
        return jsonify({"error":"Required fields missing"}),400

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""INSERT INTO registrations
        (fname,dob,gender,class_applying,guardian,phone,email,address)
        VALUES(?,?,?,?,?,?,?,?)""",
        (data['fname'],data['dob'],data['gender'],data['class'],
         data['guardian'],data['phone'],data.get('email'),data['address']))
    con.commit()
    rid = cur.lastrowid
    con.close()
    return jsonify({"success":True,"id":rid})

@app.route('/api/registrations')
def all_regs():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute("SELECT * FROM registrations ORDER BY created_at DESC").fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/export/csv')
def export_csv():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    rows = cur.execute("SELECT * FROM registrations ORDER BY created_at DESC").fetchall()
    con.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID','Name','DOB','Gender','Class','Guardian','Phone','Email','Address','Created_At'])
    writer.writerows(rows)
    output.seek(0)

    fname = f"registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(io.BytesIO(output.getvalue().encode()),
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name=fname)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)   # production में debug=False और host='0.0.0.0'
