from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client
import os

app = Flask(__name__)
CORS(app)

# এখানে আপনার ডাটা বসান
SUPABASE_URL = "https://sncrzqpvanxcylgnhete.supabase.co"
SUPABASE_KEY = "sb_secret_RViT6Rc3g1A7APnLqJmocw_skrGddOh" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/user', methods=['GET'])
def get_user():
    uid = request.args.get('uid')
    ref_by = request.args.get('ref')
    res = supabase.table("users").select("*").eq("uid", uid).execute()
    if not res.data:
        if ref_by and ref_by != uid:
            supabase.rpc('increment_referral', {'row_id': ref_by}).execute()
        supabase.table("users").insert({"uid": uid, "balance": 0}).execute()
        return jsonify({"balance": 0, "referrals": 0, "ads_watched": 0, "completed_today": []})
    u = res.data[0]
    tasks = supabase.table("tasks").select("task_id").eq("uid", uid).execute()
    return jsonify({"balance": u['balance'], "referrals": u['referrals'], "ads_watched": u['ads_watched'], "completed_today": [x['task_id'] for x in tasks.data]})

@app.route('/api/add_money', methods=['POST'])
def add_money():
    data = request.json
    supabase.rpc('add_balance', {'row_id': data['uid'], 'amount': data['amount']}).execute()
    supabase.table("tasks").insert({"uid": data['uid'], "task_id": data['task']}).execute()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
