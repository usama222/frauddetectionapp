from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from models.application import Application
from models.category import Category

from extensions import db
from models.application import Application
from models.review import Review
from models.sentiment_result import SentimentResult
from models.feedback import Feedback
from services.sentiment_service import analyze_sentiment

user_panel_bp = Blueprint('user_panel', __name__, url_prefix='/user')

def _require_user():
    if current_user.role.role_name != "User":
        return "Access Denied", 403
    return None

def _get_client_ip(req):
    # works for proxy too
    forwarded = req.headers.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return req.remote_addr

@user_panel_bp.route('/dashboard')
@login_required
def dashboard():
    denied = _require_user()
    if denied:
        return denied
    return render_template('user/dashboard.html')

@user_panel_bp.route('/')
@login_required
def user_home():
    denied = _require_user()
    if denied:
        return denied
    return redirect(url_for('user_panel.dashboard'))

@user_panel_bp.route('/apps')
@login_required
def apps_list():
    denied = _require_user()
    if denied:
        return denied

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str).strip()
    category_id = request.args.get('category_id', '', type=str).strip()

    query = Application.query

    if search:
        query = query.filter(Application.name.ilike(f"%{search}%"))

    if category_id.isdigit():
        query = query.filter(Application.category_id == int(category_id))

    applications = query.order_by(Application.created_at.desc()).paginate(page=page, per_page=10)

    categories = Category.query.order_by(Category.name.asc()).all()

    return render_template(
        'user/apps/index.html',
        applications=applications,
        categories=categories,
        search=search,
        category_id=category_id
    )

@user_panel_bp.route('/apps/<int:app_id>')
@login_required
def app_detail(app_id):
    denied = _require_user()
    if denied: return denied

    app = Application.query.get_or_404(app_id)
    reviews = Review.query.filter_by(app_id=app_id).order_by(Review.created_at.desc()).all()
    return render_template('user/apps/detail.html', app=app, reviews=reviews)

@user_panel_bp.route('/apps/<int:app_id>/review', methods=['POST'])
@login_required
def post_review(app_id):
    denied = _require_user()
    if denied: return denied

    app = Application.query.get_or_404(app_id)

    rating = int(request.form.get('rating', 0))
    review_text = (request.form.get('review_text') or '').strip()

    if not review_text or rating < 1 or rating > 5:
        return redirect(url_for('user_panel.app_detail', app_id=app_id))

    ip = _get_client_ip(request)

    #  duplicate check: same app + same ip already reviewed?
    already = Review.query.filter_by(app_id=app_id, ip_address=ip).first()
    is_dup = True if already else False

    review = Review(
        app_id=app_id,
        user_id=current_user.id,
        rating=rating,
        review_text=review_text,
        ip_address=ip,
        is_duplicate=is_dup,
        created_at=datetime.utcnow()
    )
    db.session.add(review)
    db.session.commit()

    # sentiment analysis (same as admin add review)
    label, score, fake_prob = analyze_sentiment(review_text)

    sentiment = SentimentResult(
        review_id=review.id,
        sentiment_label=label,
        sentiment_score=score,
        fake_probability=fake_prob
    )
    review.is_fake = True if fake_prob >= 0.7 else False

    db.session.add(sentiment)
    db.session.commit()

    # avg_rating recalculate of application
    from services.rating_service import recalc_app_avg_rating
    recalc_app_avg_rating(app_id)

    return redirect(url_for('user_panel.app_detail', app_id=app_id))


@user_panel_bp.route('/feedback', methods=['GET', 'POST'])
@login_required
def submit_feedback():
    denied = _require_user()
    if denied:
        return denied

    success = None
    error = None

    if request.method == 'POST':
        message = (request.form.get('message') or '').strip()

        if not message:
            error = "Feedback message cannot be empty."
        else:
            feedback = Feedback(
                user_id=current_user.id,
                message=message,
                created_at=datetime.utcnow()
            )
            db.session.add(feedback)
            db.session.commit()
            success = "Your feedback has been submitted successfully."

    return render_template('user/feedback.html', success=success, error=error)
