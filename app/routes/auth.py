from flask import Blueprint, redirect, url_for, session
from flask_login import login_user, logout_user, current_user
from app.factory import oauth, db, login_manager
from app.models import User

auth_bp = Blueprint("auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@auth_bp.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect("/")
    redirect_uri = url_for("auth.authorize", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route("/authorize")
def authorize():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.get("https://openidconnect.googleapis.com/v1/userinfo").json()

    user_id = user_info.get("sub")
    if not user_id:
        return "Authorization failed: no user ID", 400

    user_email = user_info.get("email")
    user_name = user_info.get("name", "")

    user = User.query.filter_by(id=user_id).first()
    if not user:
        user = User(id=user_id, name=user_name, email=user_email)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect("/")

@auth_bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect("/")