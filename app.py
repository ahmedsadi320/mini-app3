from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client
import os

app = Flask(__name__)
CORS(app)

# আপনার Supabase তথ্য
SUPABASE_URL = "https://sncrzqpvanxcylgnhete.supabase.co"
# এখানে আপনার Secret Key (sb_secret_...) দিন
SUPABASE_KEY = "sb_secret_RViT6Rc3g1A7APnLqJmocw_skrGddOh" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/user', methods=['GET'])
def get_user():
    uid = request.args.get('uid')
    ref_by = request.args.get('ref')
    
    if not uid:
        return jsonify({"error": "No UID"}), 400

    # ১. প্রথমে ডাটাবেসে চেক করি ইউজার আছে কি না
    res = supabase.table("users").select("*").eq("uid", uid).execute()
    
    # ২. ইউজার যদি একদম নতুন হয় (ডাটাবেসে নেই)
    if not res.data:
        # ৩. যদি তাকে কেউ রেফার করে থাকে এবং সে নিজে নিজেকে রেফার না করে
        if ref_by and ref_by != "undefined" and ref_by != uid:
            # রেফারেল বোনাস ফাংশন রান করো
            supabase.rpc('increment_referral', {'row_id': ref_by}).execute()
        
        # ৪. এবার নতুন ইউজারকে ডাটাবেসে সেভ করো
        new_user = {"uid": uid, "balance": 0, "referrals": 0, "ads_watched": 0}
        supabase.table("users").insert(new_user).execute()
        return jsonify(new_user)
    
    # ৫. পুরাতন ইউজার হলে তার তথ্য ফেরত দাও
    u = res.data[0]
    return jsonify({
        "balance": u.get('balance', 0),
        "referrals": u.get('referrals', 0),
        "ads_watched": u.get('ads_watched', 0)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
