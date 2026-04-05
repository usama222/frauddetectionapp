from flask import Blueprint, render_template
from flask_login import login_required, current_user

from extensions import db
from models.fraud_detection_log import FraudDetectionLog
from models.application import Application
from models.review import Review
from models.sentiment_result import SentimentResult
from collections import defaultdict


fraud_dashboard_bp = Blueprint(
    'fraud_dashboard',
    __name__,
    url_prefix='/admin/fraud-dashboard'
)

# =====================================================
# FRAUD DASHBOARD (SUMMARY PAGE)
# =====================================================
@fraud_dashboard_bp.route('/')
@login_required
def dashboard():
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    logs = (
        db.session.query(FraudDetectionLog, Application)
        .join(Application, FraudDetectionLog.app_id == Application.id)
        .order_by(FraudDetectionLog.analyzed_at.desc())
        .all()
    )

    total_apps = len(logs)
    fraud_apps = sum(1 for log, app in logs if log.suggested_status == "Fraud")
    suspicious_apps = sum(1 for log, app in logs if log.suggested_status == "Suspicious")
    genuine_apps = sum(1 for log, app in logs if log.suggested_status == "Genuine")

    # 🔹 MINI GRAPH DATA (simple + meaningful)
    fraud_probabilities = [log.fraud_probability for log, app in logs]
    sentiment_scores = [log.overall_sentiment_score for log, app in logs]

    total_reviews = sum(log.total_reviews for log, app in logs)
    fake_reviews = sum(log.fake_reviews for log, app in logs)

    this_month = total_reviews  # demo logic (FYP safe)
    this_week = fake_reviews

    return render_template(
        'admin/fraud_dashboard/index.html',
        logs=logs,
        total_apps=total_apps,
        fraud_apps=fraud_apps,
        suspicious_apps=suspicious_apps,
        genuine_apps=genuine_apps,
        fraud_probabilities=fraud_probabilities,
        sentiment_scores=sentiment_scores,
        this_month=this_month,
        this_week=this_week
    )

# =====================================================
#  APPLICATION FRAUD DETAIL PAGE
# =====================================================
@fraud_dashboard_bp.route('/<int:app_id>')
@login_required
def application_detail(app_id):
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    application = Application.query.get_or_404(app_id)
    fraud_log = FraudDetectionLog.query.filter_by(app_id=app_id).first_or_404()

    reviews = (
        db.session.query(Review)
        .filter(Review.app_id == app_id)
        .order_by(Review.created_at.desc())
        .all()
    )

    # ===============================
    # IDEA 1: Genuine Sentiment Distribution
    # ===============================
    genuine_positive = SentimentResult.query.join(Review).filter(
        Review.app_id == app_id,
        Review.is_fake == 0,
        SentimentResult.sentiment_label == 'Positive'
    ).count()

    genuine_negative = SentimentResult.query.join(Review).filter(
        Review.app_id == app_id,
        Review.is_fake == 0,
        SentimentResult.sentiment_label == 'Negative'
    ).count()

    genuine_neutral = SentimentResult.query.join(Review).filter(
        Review.app_id == app_id,
        Review.is_fake == 0,
        SentimentResult.sentiment_label == 'Neutral'
    ).count()

    fake_negative = SentimentResult.query.join(Review).filter(
        Review.app_id == app_id,
        Review.is_fake == 1,
        SentimentResult.sentiment_label == 'Negative'
    ).count()

    fake_neutral = SentimentResult.query.join(Review).filter(
        Review.app_id == app_id,
        Review.is_fake == 1,
        SentimentResult.sentiment_label == 'Neutral'
    ).count()

    fake_positive = SentimentResult.query.join(Review).filter(
        Review.app_id == app_id,
        Review.is_fake == 1,
        SentimentResult.sentiment_label == 'Positive'
    ).count()
    # ===============================
    # IDEA 2: Fake Review Impact
    # ===============================
    fake_percentage = round(
        (fraud_log.fake_reviews / fraud_log.total_reviews) * 100, 1
    ) if fraud_log.total_reviews else 0

    # ===============================
    # IDEA 3: Sentiment vs Rating Consistency
    # ===============================
    inconsistent_reviews = 0

    for r in reviews:
        if not r.sentiment_result:
            continue

        label = r.sentiment_result.sentiment_label
        rating = r.rating

        if (label == 'Positive' and rating <= 2) or \
           (label == 'Negative' and rating >= 4):
            inconsistent_reviews += 1

    return render_template(
        'admin/fraud_dashboard/detail.html',
        application=application,
        fraud_log=fraud_log,
        reviews=reviews,

        # IDEA 1
        genuine_positive=genuine_positive,
        genuine_negative=genuine_negative,
        genuine_neutral=genuine_neutral,

        # IDEA 2
        fake_percentage=fake_percentage,

        # IDEA 3
        inconsistent_reviews=inconsistent_reviews,

        fake_positive=fake_positive,
        fake_negative=fake_negative,
        fake_neutral=fake_neutral,

    )
