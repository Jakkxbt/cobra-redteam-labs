#!/usr/bin/env python3
import argparse
from flask import Flask, jsonify, request, session

FLAG = "FLAG{mass_assignment_privilege_escalation}" 

def create_app(safe=False):
    app = Flask(__name__)
    app.secret_key = "lab-only-session-key"
    users = {"trainee": {"username": "trainee", "password": "training", "name": "Trainee", "email": "trainee@example.test", "is_admin": False, "role": "user", "balance": 0}}

    @app.post("/login")
    def login():
        body = request.get_json(silent=True) or {}
        user = users.get(body.get("username"))
        if not user or body.get("password") != user["password"]:
            return jsonify(error="invalid credentials"), 401
        session["username"] = user["username"]
        return jsonify(message="logged in", username=user["username"])

    def current():
        name = session.get("username")
        return users.get(name) if name else None

    @app.get("/profile")
    def profile():
        user = current()
        if not user: return jsonify(error="login required"), 401
        return jsonify({k: v for k, v in user.items() if k != "password"})

    @app.post("/profile/update")
    def update():
        user = current()
        if not user: return jsonify(error="login required"), 401
        body = request.get_json(silent=True)
        if not isinstance(body, dict): return jsonify(error="JSON object required"), 400
        if safe:
            for field in ("name", "email"):
                if field in body: user[field] = body[field]
        else:
            user.update(body)
        return jsonify(message="profile updated", profile={k: v for k, v in user.items() if k != "password"})

    @app.get("/admin/flag")
    def admin_flag():
        user = current()
        if not user: return jsonify(error="login required"), 401
        if not user.get("is_admin") and user.get("role") != "admin": return jsonify(error="admin only"), 403
        return jsonify(flag=FLAG)
    return app

def main():
    parser = argparse.ArgumentParser(description="Mass-assignment privilege escalation training lab")
    parser.add_argument("--safe", action="store_true", help="run the allowlisted safe implementation")
    parser.add_argument("--port", type=int, default=18122, help="localhost port (default: 18122)")
    args = parser.parse_args()
    app = create_app(args.safe)
    print(f"Mass-assignment lab ({'safe' if args.safe else 'vulnerable'}) listening at http://127.0.0.1:{args.port}", flush=True)
    app.run(host="127.0.0.1", port=args.port, debug=False)

if __name__ == "__main__": main()
