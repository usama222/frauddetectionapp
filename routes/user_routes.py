from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from models.user import User
from extensions import db

user_bp = Blueprint(
    'users',
    __name__,
    url_prefix='/admin/users'
)

# -------------------------
# LIST USERS
# -------------------------
@user_bp.route('/')
@login_required
def list_users():
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    query = User.query.join(User.role).filter(
        User.role.has(role_name='User')
    )

    if search:
        query = query.filter(
            User.name.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%")
        )

    users = query.order_by(
        User.created_at.desc()
    ).paginate(page=page, per_page=10)

    return render_template(
        'admin/users/index.html',
        users=users,
        search=search
    )


# -------------------------
# TOGGLE STATUS
# -------------------------
@user_bp.route('/toggle-status/<int:id>')
@login_required
def toggle_user_status(id):
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    user = User.query.get_or_404(id)
    user.status = not user.status
    db.session.commit()

    return redirect(url_for('users.list_users'))
