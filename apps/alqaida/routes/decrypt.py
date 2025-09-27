from flask import request, render_template
from .. import alqaida_blueprint
from ..alqaida import untwist_and_decrypt

@alqaida_blueprint.route("/decrypt", methods=["GET", "POST"])
def decrypt_endpoint():
    result = None
    error = None
    text = ""
    if request.method == "POST":
        if request.is_json:
            data = request.get_json(silent=True) or {}
            text = data.get("text", "")
        else:
            text = request.form.get("text", "")
        if not isinstance(text, str) or text.strip() == "":
            error = "Please paste a wordified message to decrypt."
        else:
            try:
                result = untwist_and_decrypt(text)
            except Exception as e:
                error = f"{e.__class__.__name__}: {e}"
    return render_template("decrypt.html", page_title="Decrypt", text=text, result=result, error=error)
