@app.route('/api/user', methods=['GET'])
def get_user():
    uid = request.args.get('uid')
    ref_by = request.args.get('ref')
    
    # প্রথমে চেক করি ইউজার আগে থেকে আছে কি না
    res = supabase.table("users").select("*").eq("uid", uid).execute()
    
    if not res.data:
        # ইউজার যদি একদম নতুন হয়, তবেই রেফারেল বোনাস দাও
        if ref_by and ref_by != uid:
            # রেফারেল বোনাস দেওয়ার ফাংশন কল
            supabase.rpc('increment_referral', {'row_id': ref_by}).execute()
        
        # এবার নতুন ইউজারকে ডাটাবেসে সেভ করো
        supabase.table("users").insert({"uid": uid, "balance": 0}).execute()
        
        # নতুন ইউজারের জন্য ডাটা রিটার্ন
        return jsonify({"balance": 0, "referrals": 0, "ads_watched": 0, "completed_today": []})
    
    # পুরাতন ইউজার হলে তার তথ্য দাও
    u = res.data[0]
    tasks = supabase.table("tasks").select("task_id").eq("uid", uid).execute()
    return jsonify({
        "balance": u['balance'], 
        "referrals": u['referrals'], 
        "ads_watched": u['ads_watched'], 
        "completed_today": [x['task_id'] for x in tasks.data]
    })
