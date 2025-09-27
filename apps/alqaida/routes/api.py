# apps/alqaida/routes/api.py
from flask import request, jsonify
from .. import alqaida_blueprint
from ..alqaida import encrypt_and_twist, untwist_and_decrypt

def _bad_request(msg: str):
    return jsonify(ok=False, error=msg), 400

@alqaida_blueprint.post("/api/encrypt")
def api_encrypt():
    """
    JSON API: POST /alqaida/api/encrypt
    body: { "text": "<plaintext>" }
    returns: { "ok": true, "result": "<wordified + notice>" }
    """
    if not request.is_json:
        return _bad_request("Content-Type must be application/json")
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if not isinstance(text, str) or text.strip() == "":
        return _bad_request("Provide JSON {'text': '<message>'}")
    try:
        result = encrypt_and_twist(text)
        return jsonify(ok=True, result=result)
    except Exception as e:
        return _bad_request(f"{e.__class__.__name__}: {e}")

@alqaida_blueprint.post("/api/decrypt")
def api_decrypt():
    """
    JSON API: POST /alqaida/api/decrypt
    body: { "text": "<wordified [+ optional notice]>" }
    returns: { "ok": true, "result": "<plaintext>" }
    """
    if not request.is_json:
        return _bad_request("Content-Type must be application/json")
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    if not isinstance(text, str) or text.strip() == "":
        return _bad_request("Provide JSON {'text': '<wordified message>'}")
    try:
        result = untwist_and_decrypt(text)
        return jsonify(ok=True, result=result)
    except Exception as e:
        return _bad_request(f"{e.__class__.__name__}: {e}")
