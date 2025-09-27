from flask import request, render_template
from .. import alqaida_blueprint
from ..alqaida import encrypt_and_twist

@alqaida_blueprint.route("/encrypt", methods=["GET", "POST"])
def encrypt_endpoint():
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
            error = "Please enter a message to encrypt."
        else:
            try:
                result = encrypt_and_twist(text)
            except Exception as e:
                error = f"{e.__class__.__name__}: {e}"
    return render_template("encrypt.html", page_title="Encrypt", text=text, result=result, error=error)
