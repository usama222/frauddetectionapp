from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from extensions import db
from models.feedback import Feedback

user_feedback_bp = Blueprint('user_feedback', __name__, url_prefix='/user/feedback')


def _require_user():
    if current_user.role.role_name != "User":
        return "Access Denied", 403
    return None


def _get_client_ip(req):
    forwarded = req.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return req.remote_addr


# -------------------------
# LIST MY FEEDBACK
# -------------------------
@user_feedback_bp.route('/')
@login_required
def index():
    denied = _require_user()
    if denied:
        return denied

    feedbacks = Feedback.query \
        .filter_by(user_id=current_user.id) \
        .order_by(Feedback.created_at.desc()) \
        .all()

    return render_template('user/feedback/index.html', feedbacks=feedbacks)


# -------------------------
# SUBMIT FEEDBACK
# -------------------------
@user_feedback_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    denied = _require_user()
    if denied:
        return denied

    if request.method == 'POST':
        subject = (request.form.get('subject') or '').strip() or None
        message = (request.form.get('message') or '').strip()
        rating_raw = request.form.get('rating', '').strip()
        rating = int(rating_raw) if rating_raw.isdigit() and 1 <= int(rating_raw) <= 5 else None

        if not message:
            flash("Feedback message is required.", "danger")
            return render_template('user/feedback/create.html')

        feedback = Feedback(
            user_id=current_user.id,
            subject=subject,
            message=message,
            rating=rating,
            ip_address=_get_client_ip(request),
            created_at=datetime.utcnow()
        )
        db.session.add(feedback)
        db.session.commit()

        flash("Your feedback has been submitted successfully.", "success")
        return redirect(url_for('user_feedback.index'))

    return render_template('user/feedback/create.html')
