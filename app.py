from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Render-এর ডিস্ক স্টোরেজ ব্যবহারের জন্য পাথ
DB_PATH = '/opt/render/project/src/data/database.db'

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (uid TEXT PRIMARY KEY, balance REAL DEFAULT 0, referrals INTEGER DEFAULT 0, ads_watched INTEGER DEFAULT 0)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS tasks 
                 (uid TEXT, task_id TEXT)''')
    conn.close()

@app.route('/api/user', methods=['GET'])
def get_user():
    uid = request.args.get('uid')
    ref_by = request.args.get('ref')
    
    conn = sqlite3.connect(DB_PATH)
    user = conn.execute('SELECT balance, referrals, ads_watched FROM users WHERE uid=?', (uid,)).fetchone()
    
    if not user:
        if ref_by and ref_by != uid:
            conn.execute('UPDATE users SET balance = balance + 40, referrals = referrals + 1 WHERE uid=?', (ref_by,))
        conn.execute('INSERT INTO users (uid, balance) VALUES (?, ?)', (uid, 0))
        conn.commit()
        user = (0, 0, 0)
        
    completed = conn.execute('SELECT task_id FROM tasks WHERE uid=?', (uid,)).fetchall()
    conn.close()
    
    return jsonify({
        "balance": user[0], "referrals": user[1], "ads_watched": user[2],
        "completed_today": [x[0] for x in completed]
    })

@app.route('/api/add_money', methods=['POST'])
def add_money():
    data = request.json
    uid, amount, task = data['uid'], data['amount'], data['task']
    conn = sqlite3.connect(DB_PATH)
    conn.execute('UPDATE users SET balance = balance + ?, ads_watched = ads_watched + 1 WHERE uid=?', (amount, uid))
    conn.execute('INSERT INTO tasks (uid, task_id) VALUES (?, ?)', (uid, task))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
