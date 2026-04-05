from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, login_required, current_user, logout_user
from extensions import db
from werkzeug.security import check_password_hash
from sqlalchemy import func
from datetime import datetime
from collections import Counter
from collections import defaultdict


from models.application import Application
from models.feedback import Feedback
from models.fraud_detection_log import FraudDetectionLog
from models.review import Review
from models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/admin')

@auth_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.role.role_name == "Admin" and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('auth.admin_dashboard'))

        return render_template('admin/auth/login.html', error="Invalid admin credentials")

    return render_template('admin/auth/login.html')


@auth_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    # =======================
    # SUMMARY COUNTS
    # =======================
    total_users = db.session.query(User).count()
    total_apps = db.session.query(Application).count()
    total_reviews = db.session.query(Review).count()
    fake_reviews = db.session.query(Review).filter_by(is_fake=1).count()

    # Fraud stats
    fraud_apps = FraudDetectionLog.query.filter_by(suggested_status='Fraud').count()
    suspicious_apps = FraudDetectionLog.query.filter_by(suggested_status='Suspicious').count()
    genuine_apps = FraudDetectionLog.query.filter_by(suggested_status='Genuine').count()

    # =======================
    # LATEST REVIEWS
    # =======================
    latest_reviews = (
        db.session.query(
            Review.review_text,
            Review.rating,
            Review.is_fake,
            Review.created_at,
            Application.name.label("app_name"),
            User.name.label('user_name'),
            User.email.label("user_email"),
        )
        .join(Application, Review.app_id == Application.id)
        .join(User, Review.user_id == User.id)
        .order_by(Review.created_at.desc())
        .limit(5)
        .all()
    )


    # =======================
    # RECENT FRAUD ANALYSIS
    # =======================
    recent_apps = (
        db.session.query(FraudDetectionLog, Application)
        .join(Application, FraudDetectionLog.app_id == Application.id)
        .order_by(FraudDetectionLog.analyzed_at.desc())
        .limit(5)
        .all()
    )
    # =======================
    # USERS REGISTRATION (MONTH-WISE)
    # =======================
    user_months = Counter(
        u.created_at.strftime('%Y-%m')
        for u in User.query.all()
    )

    user_chart_labels = sorted(user_months.keys())
    user_chart_data = [user_months[m] for m in user_chart_labels]

    review_stats = defaultdict(lambda: {"fake": 0, "genuine": 0})

    reviews = Review.query.filter(Review.created_at.isnot(None)).all()

    for r in reviews:
        month = r.created_at.strftime('%b')
        if r.is_fake:
            review_stats[month]["fake"] += 1
        else:
            review_stats[month]["genuine"] += 1

    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    labels = []
    fake_data = []
    genuine_data = []

    for m in month_order:
        if m in review_stats:
            labels.append(m)
            fake_data.append(-review_stats[m]["fake"])
            genuine_data.append(review_stats[m]["genuine"])

    # =======================
    # USER REGISTRATION TREND
    # =======================
    users = User.query.filter(User.created_at.isnot(None)).order_by(User.created_at.desc()).all()

    monthly_counts = Counter(
        u.created_at.strftime('%b') for u in users
    )

    # Order months properly
    month_order = ['Jan','Feb','Mar','Apr','May','Jun',
                   'Jul','Aug','Sep','Oct','Nov','Dec']

    user_month_labels = []
    monthly_users = []
    cumulative_users = []

    total = 0
    for m in month_order:
        if m in monthly_counts:
            count = monthly_counts[m]
            total += count
            user_month_labels.append(m)
            monthly_users.append(count)
            cumulative_users.append(total)


    # lastest users
    latest_users = users[:10]

    # =======================
    # LATEST Feedbacks
    # =======================
    latest_feedbacks = (
        db.session.query(Feedback)
        .order_by(Feedback.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_apps=total_apps,
        total_reviews=total_reviews,
        fake_reviews=fake_reviews,
        fraud_apps=fraud_apps,
        suspicious_apps=suspicious_apps,
        genuine_apps=genuine_apps,
        latest_reviews=latest_reviews,
        recent_apps=recent_apps,
        user_chart_labels=user_chart_labels,
        user_chart_data=user_chart_data,
        # review_chart_labels=review_chart_labels,
        # review_chart_data=review_chart_data,
        user_month_labels=user_month_labels,
        monthly_users=monthly_users,
        cumulative_users=cumulative_users,
        # review_activity_labels=review_activity_labels,
        # review_activity_counts=review_activity_counts,
        review_labels=labels,
        fake_review_data=fake_data,
        genuine_review_data=genuine_data,
        latest_users=latest_users,
        latest_feedbacks = latest_feedbacks
    )
# def admin_dashboard():
#     if current_user.role.role_name != "Admin":
#         return "Access Denied", 403,
#
#     # =======================
#     # SUMMARY COUNTS
#     # =======================
#     total_users = db.session.query(User).count()
#     total_apps = db.session.query(Application).count()
#     total_reviews = db.session.query(Review).count()
#     fake_reviews = db.session.query(Review).filter_by(is_fake=1).count()
#
#     # Fraud stats
#     fraud_apps = FraudDetectionLog.query.filter_by(suggested_status='Fraud').count()
#     suspicious_apps = FraudDetectionLog.query.filter_by(suggested_status='Suspicious').count()
#     genuine_apps = FraudDetectionLog.query.filter_by(suggested_status='Genuine').count()
#
#     # =======================
#     # USERS GROWTH (⬆⬇)
#     # =======================
#     now = datetime.now()
#     current_month = now.month
#     current_year = now.year
#
#     last_month = current_month - 1 or 12
#     last_month_year = current_year if current_month != 1 else current_year - 1
#
#     this_month_users = db.session.query(User).filter(
#         func.month(User.created_at) == current_month,
#         func.year(User.created_at) == current_year
#     ).count()
#
#     last_month_users = db.session.query(User).filter(
#         func.month(User.created_at) == last_month,
#         func.year(User.created_at) == last_month_year
#     ).count()
#
#     if last_month_users == 0:
#         user_growth = 100 if this_month_users > 0 else 0
#     else:
#         user_growth = round(
#             ((this_month_users - last_month_users) / last_month_users) * 100, 1
#         )
#
#     # =======================
#     # USERS BY MONTH (GRAPH)
#     # =======================
#     users_by_month = (
#         db.session.query(
#             func.month(User.created_at).label("month"),
#             func.count(User.id).label("total")
#         )
#         .group_by(func.month(User.created_at))
#         .order_by(func.month(User.created_at))
#         .all()
#     )
#
#     users_chart_labels = [f"Month {m}" for m, c in users_by_month]
#     users_chart_data = [c for m, c in users_by_month]
#
#     # =======================
#     # LATEST REVIEWS
#     # =======================
#     latest_reviews = (
#         db.session.query(Review)
#         .order_by(Review.created_at.desc())
#         .limit(5)
#         .all()
#     )
#
#     # =======================
#     # RECENT FRAUD ANALYSIS
#     # =======================
#     recent_apps = (
#         db.session.query(FraudDetectionLog, Application)
#         .join(Application, FraudDetectionLog.app_id == Application.id)
#         .order_by(FraudDetectionLog.analyzed_at.desc())
#         .limit(5)
#         .all()
#     )
#
#     return render_template(
#         'admin/dashboard.html',
#
#         # COUNTS
#         total_users=total_users,
#         total_apps=total_apps,
#         total_reviews=total_reviews,
#         fake_reviews=fake_reviews,
#
#         # FRAUD
#         fraud_apps=fraud_apps,
#         suspicious_apps=suspicious_apps,
#         genuine_apps=genuine_apps,
#
#         # USERS GROWTH
#         user_growth=user_growth,
#
#         # CHART
#         users_chart_labels=users_chart_labels,
#         users_chart_data=users_chart_data,
#
#         # TABLES
#         latest_reviews=latest_reviews,
#         recent_apps=recent_apps
#     )


@auth_bp.route('/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('auth.admin_login'))
