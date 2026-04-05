import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models.review import Review
from models.sentiment_result import SentimentResult
from models.user import User
from models.application import Application
from services.sentiment_service import analyze_sentiment


def seed_reviews_and_sentiments():

    user = User.query.filter_by(role_id=2).first()
    if not user:
        print("❌ No user found with role_id=2")
        return

    apps = Application.query.limit(3).all()
    if not apps:
        print("❌ No applications found")
        return

    dummy_reviews = [
        ("This app is very good and helpful", 5),
        ("Worst app, full of bugs and scam", 1),
        ("Average experience, nothing special", 3),
        ("Excellent app, fast and reliable", 5),
        ("Terrible performance, waste of time", 1),
    ]

    for app in apps:
        for text, rating in dummy_reviews:
            review = Review(
                user_id=user.id,
                app_id=app.id,
                review_text=text,
                rating=rating
            )
            db.session.add(review)
            db.session.flush()  # review.id mil jata hai

            label, score, fake_prob = analyze_sentiment(text)

            sentiment = SentimentResult(
                review_id=review.id,
                sentiment_label=label,
                sentiment_score=score,
                fake_probability=fake_prob
            )

            db.session.add(sentiment)

    db.session.commit()
    print(" Dummy reviews & sentiment results inserted")


if __name__ == "__main__":
    with app.app_context():
        seed_reviews_and_sentiments()
