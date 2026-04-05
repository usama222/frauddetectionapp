from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import or_

from models.feedback import Feedback
from models.user import User

feedback_bp = Blueprint(
    'feedback',
    __name__,
    url_prefix='/admin/feedback'
)

# -------------------------
# LIST FEEDBACK (ADMIN)
# -------------------------
@feedback_bp.route('/')
@login_required
def list_feedback():
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    query = Feedback.query.join(User)

    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                Feedback.message.ilike(f"%{search}%")
            )
        )

    feedbacks = query.order_by(
        Feedback.created_at.desc()
    ).paginate(page=page, per_page=10)

    return render_template(
        'admin/feedback/index.html',
        feedbacks=feedbacks,
        search=search
    )
