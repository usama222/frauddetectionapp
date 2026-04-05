from extensions import db
from models.review import Review
from models.sentiment_result import SentimentResult
from models.fraud_detection_log import FraudDetectionLog

def analyze_application_fraud(app_id):
    # -------------------------
    # Fetch reviews of app
    # -------------------------
    reviews = Review.query.filter_by(app_id=app_id).all()

    total_reviews = len(reviews)
    if total_reviews == 0:
        return None

    fake_reviews = 0
    positive = 0
    negative = 0
    neutral = 0

    sentiment_sum = 0
    sentiment_count = 0

    for review in reviews:
        if review.is_fake:
            fake_reviews += 1
            continue

        sentiment = review.sentiment_result
        if not sentiment:
            continue

        if sentiment.sentiment_label == "Positive":
            positive += 1
        elif sentiment.sentiment_label == "Negative":
            negative += 1
        else:
            neutral += 1

        sentiment_sum += sentiment.sentiment_score
        sentiment_count += 1

    # -------------------------
    # Calculations
    # -------------------------
    fraud_probability = round(fake_reviews / total_reviews, 2)

    overall_sentiment_score = (
        round(sentiment_sum / sentiment_count, 2)
        if sentiment_count > 0 else 0
    )

    # -------------------------
    # Suggested Status
    # -------------------------
    if fraud_probability >= 0.6:
        suggested_status = "Fraud"
    elif fraud_probability >= 0.3:
        suggested_status = "Suspicious"
    else:
        suggested_status = "Genuine"

    # -------------------------
    # Insert / Update Log
    # -------------------------
    log = FraudDetectionLog.query.filter_by(app_id=app_id).first()

    if not log:
        log = FraudDetectionLog(app_id=app_id)

    log.total_reviews = total_reviews
    log.fake_reviews = fake_reviews
    log.positive_reviews = positive
    log.negative_reviews = negative
    log.neutral_reviews = neutral
    log.fraud_probability = fraud_probability
    log.overall_sentiment_score = overall_sentiment_score
    log.suggested_status = suggested_status

    db.session.add(log)
    db.session.commit()

    return log
