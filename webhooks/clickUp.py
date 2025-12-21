import hmac
import hashlib
import os
import json
from flask import Flask, request, abort, jsonify

app = Flask(__name__)


CLICKUP_WEBHOOK_SECRET = os.environ.get("CLICKUP_WEBHOOK_SECRET", "troque_por_seu_secret")

USER_MAP = {
    "123456": "dayvid", 
}


CATALOGO = {
    "feat_pequena": 400,
    "feat_media": 1600,
    "feat_grande": 6400,
    "code_review_simples": 15,
    "code_review_detalhado": 25,
    "code_review_excepcional": 40
}

def verify_signature(raw_body: bytes, signature_header: str) -> bool:
    if not signature_header:
        return False
    computed = hmac.new(
        CLICKUP_WEBHOOK_SECRET.encode('utf-8'),
        raw_body,
        hashlib.sha256
    ).hexdigest()
   
    return hmac.compare_digest(computed, signature_header)

def award_xp(club_user_id: str, xp: int, reason: str, proof_url: str = None):
    print(f"Awarding {xp} XP to {club_user_id} for {reason} (proof: {proof_url})")
    return True

@app.route("/api/clickup/webhook", methods=["POST"])
def clickup_webhook():
    raw = request.get_data()
    sig = request.headers.get("X-Signature") or request.headers.get("x-signature")
    if not verify_signature(raw, sig):
        abort(401, "Invalid signature")

    payload = request.json  
    event = payload.get("event")
    task = payload.get("task") or payload.get("task_old") or payload.get("task_new")
    if not task:
        return jsonify({"ok": True})

    status = task.get("status", {}).get("status")
    custom_fields = task.get("custom_fields", [])
    feat_size = None
    for f in custom_fields:
        if f.get("name", "").lower() in ("feat size", "feat_size", "tamanho feat"):
            feat_size = f.get("value") 

    if status and status.lower() in ("done", "completed") or feat_size:
        assignees = task.get("assignees", []) or []
        xp_per_person = 0
        if feat_size:
            if "grande" in str(feat_size).lower():
                xp_per_person = CATALOGO["feat_grande"]
            elif "média" in str(feat_size).lower() or "media" in str(feat_size).lower():
                xp_per_person = CATALOGO["feat_media"]
            else:
                xp_per_person = CATALOGO["feat_pequena"]
        else:
            xp_per_person = CATALOGO["feat_media"]

        proof = f"https://app.clickup.com/t/{task.get('id')}"
        for a in assignees:
            clickup_user_id = str(a.get("id"))
            club_id = USER_MAP.get(clickup_user_id)
            if club_id:
                award_xp(club_id, xp_per_person, reason="Feat concluída (ClickUp)", proof_url=proof)
            else:
                print(f"Unmapped ClickUp user: {clickup_user_id}")

    return jsonify({"ok": True})
