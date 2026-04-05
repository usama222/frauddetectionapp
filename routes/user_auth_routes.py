from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from extensions import db
from models.user import User
from models.role import Role

user_auth_bp = Blueprint('user_auth', __name__, url_prefix='/user')

@user_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # If already logged in, send to user apps
    if current_user.is_authenticated and current_user.role.role_name == "User":
        return redirect(url_for('user_panel.apps_list'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not name or not email or not password:
            return render_template('user/auth/register.html', error="All fields are required")

        existing = User.query.filter_by(email=email).first()
        if existing:
            return render_template('user/auth/register.html', error="Email already exists")

        user_role = Role.query.filter_by(role_name='User').first()
        if not user_role:
            user_role = Role(role_name='User', status=True, created_at=datetime.utcnow())
            db.session.add(user_role)
            db.session.commit()

        u = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role_id=user_role.id,
            status=True,
            created_at=datetime.utcnow()
        )
        db.session.add(u)
        db.session.commit()

        login_user(u)
        return redirect(url_for('user_panel.dashboard'))

    return render_template('user/auth/register.html')


@user_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, send to user apps
    if current_user.is_authenticated and current_user.role.role_name == "User":
        return redirect(url_for('user_panel.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(email=email).first()

        if user and user.role.role_name == "User" and user.status and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('user_panel.apps_list'))

        return render_template('user/auth/login.html', error="Invalid user credentials")

    return render_template('user/auth/login.html')


@user_auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_auth.login'))