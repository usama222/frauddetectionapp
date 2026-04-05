from extensions import db
from datetime import datetime

class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # RELATIONSHIP
    user = db.relationship('User', backref='feedbacks')

    def __repr__(self):
        return f"<Feedback {self.id} by User {self.user_id}>"
