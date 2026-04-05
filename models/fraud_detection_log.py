from extensions import db
from datetime import datetime

class FraudDetectionLog(db.Model):
    __tablename__ = 'fraud_detection_log'

    id = db.Column(db.Integer, primary_key=True)

    app_id = db.Column(
        db.Integer,
        db.ForeignKey('applications.id'),
        nullable=False
    )

    # -------- Review Statistics --------
    total_reviews = db.Column(db.Integer, default=0)
    fake_reviews = db.Column(db.Integer, default=0)

    positive_reviews = db.Column(db.Integer, default=0)
    negative_reviews = db.Column(db.Integer, default=0)
    neutral_reviews = db.Column(db.Integer, default=0)

    # -------- Core Analytics --------
    fraud_probability = db.Column(db.Float, default=0)   # fake_ratio
    overall_sentiment_score = db.Column(db.Float, default=0)

    # -------- System Suggestion --------
    suggested_status = db.Column(db.String(50))  # Genuine | Suspicious | Fraud

    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # -------- Relationships --------
    application = db.relationship('Application')

    # def __repr__(self):
    #     return f"<FraudDetectionLog app_id={self.app_id} status={self.suggested_status}>"
