from sqlalchemy import func
from extensions import db
from models.review import Review
from models.application import Application

def recalc_app_avg_rating(app_id: int) -> float:
    avg = (
        db.session.query(func.coalesce(func.avg(Review.rating), 0))
        .filter(Review.app_id == app_id)
        .filter(Review.is_duplicate == 0)   # exclude duplicates
        .scalar()
    )

    avg_val = round(float(avg or 0), 2)

    app = Application.query.get(app_id)
    if app:
        app.avg_rating = avg_val
        db.session.commit()

    return avg_val