from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from extensions import db
from models.review import Review
from models.user import User
from models.application import Application
from models.sentiment_result import SentimentResult
from services.sentiment_service import analyze_sentiment
from services.fraud_detection_service import analyze_application_fraud

admin_review_bp = Blueprint(
    'admin_reviews',
    __name__,
    url_prefix='/admin/reviews'
)

@admin_review_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_review():
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    applications = Application.query.all()
    users = User.query.filter(User.role.has(role_name='User')).all()

    if request.method == 'POST':
        app_id = request.form['app_id']
        user_id = request.form['user_id']
        rating = int(request.form['rating'])
        review_text = request.form['review_text']

        review = Review(
            app_id=app_id,
            user_id=user_id,
            rating=rating,
            review_text=review_text
        )
        db.session.add(review)
        db.session.commit()

        label, score, fake_prob = analyze_sentiment(review_text)

        sentiment = SentimentResult(
            review_id=review.id,
            sentiment_label=label,
            sentiment_score=score,
            fake_probability=fake_prob
        )

        review.is_fake = True if fake_prob >= 0.65 else False

        db.session.add(sentiment)
        db.session.commit()

        analyze_application_fraud(app_id)

        return redirect(url_for('admin_reviews.add_review'))

    return render_template(
        'admin/reviews/add_temp.html',
        applications=applications,
        users=users
    )
