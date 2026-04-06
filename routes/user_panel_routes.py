from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from models.application import Application
from models.category import Category

from extensions import db
from models.review import Review
from models.sentiment_result import SentimentResult
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

    uid = current_user.id

    # ── KPI CARDS ──────────────────────────────────────────
    total_apps     = Application.query.count()
    total_reviews  = Review.query.filter_by(user_id=uid).count()
    duplicate_count = Review.query.filter_by(user_id=uid, is_duplicate=True).count()
    fake_count     = Review.query.filter_by(user_id=uid, is_fake=True).count()

    # ── SENTIMENT PIE ──────────────────────────────────────
    sentiment_rows = (
        db.session.query(SentimentResult.sentiment_label, func.count(SentimentResult.id))
        .join(Review, Review.id == SentimentResult.review_id)
        .filter(Review.user_id == uid)
        .group_by(SentimentResult.sentiment_label)
        .all()
    )
    sentiment_map = {label: count for label, count in sentiment_rows}
    sentiment_labels = list(sentiment_map.keys())
    sentiment_data   = list(sentiment_map.values())

    # ── BAR CHART: top 5 apps reviewed by user ─────────────
    top_apps_rows = (
        db.session.query(Application.name, func.count(Review.id).label('cnt'))
        .join(Review, Review.app_id == Application.id)
        .filter(Review.user_id == uid)
        .group_by(Application.id, Application.name)
        .order_by(func.count(Review.id).desc())
        .limit(5)
        .all()
    )
    bar_labels = [r.name for r in top_apps_rows]
    bar_data   = [r.cnt  for r in top_apps_rows]

    # ── RECENT ACTIVITY (last 5 reviews) ───────────────────
    recent_reviews = (
        Review.query
        .options(joinedload(Review.application), joinedload(Review.sentiment_result))
        .filter_by(user_id=uid)
        .order_by(Review.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        'user/dashboard.html',
        total_apps=total_apps,
        total_reviews=total_reviews,
        duplicate_count=duplicate_count,
        fake_count=fake_count,
        sentiment_labels=sentiment_labels,
        sentiment_data=sentiment_data,
        bar_labels=bar_labels,
        bar_data=bar_data,
        recent_reviews=recent_reviews,
    )

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

    reviews = (
        Review.query
        .options(joinedload(Review.user), joinedload(Review.sentiment_result))
        .filter_by(app_id=app_id)
        .order_by(Review.created_at.desc())
        .all()
    )

    total_reviews  = len(reviews)
    fake_count     = sum(1 for r in reviews if r.is_fake)
    genuine_count  = total_reviews - fake_count
    duplicate_count = sum(1 for r in reviews if r.is_duplicate)

    # sentiment distribution (genuine reviews only)
    sentiment_map = {'Positive': 0, 'Neutral': 0, 'Negative': 0}
    for r in reviews:
        if not r.is_fake and r.sentiment_result:
            lbl = r.sentiment_result.sentiment_label
            if lbl in sentiment_map:
                sentiment_map[lbl] += 1

    # rating distribution 1-5
    rating_dist = {i: 0 for i in range(1, 6)}
    for r in reviews:
        if r.rating and 1 <= r.rating <= 5:
            rating_dist[r.rating] += 1

    return render_template(
        'user/apps/detail.html',
        app=app,
        reviews=reviews,
        total_reviews=total_reviews,
        fake_count=fake_count,
        genuine_count=genuine_count,
        duplicate_count=duplicate_count,
        sentiment_map=sentiment_map,
        rating_dist=rating_dist,
    )

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


@user_panel_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    denied = _require_user()
    if denied:
        return denied

    if request.method == 'POST':
        name     = (request.form.get('name') or '').strip()
        email    = (request.form.get('email') or '').strip().lower()
        password = (request.form.get('password') or '').strip()
        confirm  = (request.form.get('confirm_password') or '').strip()

        if not name or not email:
            flash("Name and email are required.", "danger")
            return render_template('user/profile.html')

        # check email taken by another user
        from models.user import User
        existing = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing:
            flash("Email is already in use by another account.", "danger")
            return render_template('user/profile.html')

        current_user.name  = name
        current_user.email = email

        if password:
            if password != confirm:
                flash("Passwords do not match.", "danger")
                return render_template('user/profile.html')
            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return render_template('user/profile.html')
            from werkzeug.security import generate_password_hash
            current_user.password = generate_password_hash(password)

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for('user_panel.profile'))

    return render_template('user/profile.html')
