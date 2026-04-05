# models/sentiment_result.py
from extensions import db
from datetime import datetime

class SentimentResult(db.Model):
    __tablename__ = 'sentiment_results'

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), unique=True)
    sentiment_label = db.Column(db.String(50))
    sentiment_score = db.Column(db.Float)
    fake_probability = db.Column(db.Float)
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)

    review = db.relationship(
        'Review',
        back_populates='sentiment_result'
    )
