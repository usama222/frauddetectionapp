from flask import Blueprint, render_template, request,redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from extensions import db

from models.review import Review
from models.sentiment_result import SentimentResult

review_bp = Blueprint(
    'reviews',
    __name__,
    url_prefix='/admin/reviews'
)

# -------------------------
# LIST REVIEWS + SENTIMENT
# -------------------------
@review_bp.route('/')
@login_required
def list_reviews():
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    page = request.args.get('page', 1, type=int)

    reviews = Review.query \
        .options(joinedload(Review.user),
                 joinedload(Review.application),
                 joinedload(Review.sentiment_result)) \
        .order_by(Review.created_at.desc()) \
        .paginate(page=page, per_page=10)

    return render_template(
        'admin/reviews/index.html',
        reviews=reviews
    )

@review_bp.route('/duplicates')
@login_required
def duplicate_reviews():
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    page = request.args.get('page', 1, type=int)

    reviews = Review.query \
        .options(joinedload(Review.user),
                 joinedload(Review.application),
                 joinedload(Review.sentiment_result)) \
        .filter(Review.is_duplicate == 1) \
        .order_by(Review.created_at.desc()) \
        .paginate(page=page, per_page=10)

    return render_template('admin/reviews/duplicates.html', reviews=reviews)

@review_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_review(id):
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    r = Review.query.get_or_404(id)
    app_id = r.app_id
    db.session.delete(r)
    db.session.commit()

    #avg_rating recalculate of application
    from services.rating_service import recalc_app_avg_rating
    recalc_app_avg_rating(app_id)

    # fraud log refresh — keeps fraud dashboard always updated
    from services.fraud_detection_service import analyze_application_fraud
    analyze_application_fraud(app_id)

    # redirect back to whichever page called delete
    ref = request.args.get('from', 'duplicate')
    if ref == 'fake':
        return redirect(url_for('reviews.fake_reviews'))
    return redirect(url_for('reviews.duplicate_reviews'))


@review_bp.route('/fake')
@login_required
def fake_reviews():
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    page = request.args.get('page', 1, type=int)

    reviews = Review.query \
        .options(joinedload(Review.user),
                 joinedload(Review.application),
                 joinedload(Review.sentiment_result)) \
        .filter(Review.is_fake == True) \
        .order_by(Review.created_at.desc()) \
        .paginate(page=page, per_page=10)

    return render_template('admin/reviews/fake.html', reviews=reviews)