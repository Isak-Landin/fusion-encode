# app.py (only the changed bits)

from flask import Flask, jsonify, render_template
from dotenv import load_dotenv
from apps.alqaida import alqaida_blueprint

def create_app():
    load_dotenv()
    _app = Flask(__name__)  # uses default templates/ and static/ at project root

    _app.config["JSON_SORT_KEYS"] = False
    _app.config.setdefault("SECRET_KEY", "change-me")

    @_app.get("/")
    def home():
        return render_template("index.html", page_title="Fusion")

    @_app.get("/healthz")
    def healthz():
        return "ok", 200

    _app.register_blueprint(alqaida_blueprint, url_prefix="/alqaida")

    PLAUSIBLE = "https://plausible.io"  # if self-hosting, e.g. "https://analytics.fusionencode.com"

    @_app.after_request
    def add_security_headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "no-referrer-when-downgrade")
        resp.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        resp.headers.setdefault("X-XSS-Protection", "1; mode=block")

        if resp.mimetype == "text/html":
            csp = [
                "default-src 'self'",
                "img-src 'self' data:",
                "style-src 'self'",
                "font-src 'self'",
                f"script-src 'self' {PLAUSIBLE}",
                f"connect-src 'self' {PLAUSIBLE}",
                "base-uri 'none'",
                "form-action 'self'",
                "object-src 'none'"
            ]
            resp.headers["Content-Security-Policy"] = "; ".join(csp)
        return resp

    return _app

app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5911, debug=True)