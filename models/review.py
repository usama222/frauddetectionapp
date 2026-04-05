# models/review.py
from extensions import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    app_id = db.Column(db.Integer, db.ForeignKey('applications.id'))
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer,default=False)
    is_fake = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(45), nullable=True)
    is_duplicate = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')
    application = db.relationship('Application')
    sentiment_result = db.relationship(
        'SentimentResult',
        uselist=False,
        back_populates='review'

    )