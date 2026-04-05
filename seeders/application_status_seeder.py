from app import create_app
from extensions import db
from models.application_status import ApplicationStatus

app = create_app()

with app.app_context():

    statuses = [
        "Pending",
        "Genuine",
        "Suspicious",
        "Fraud"
    ]

    for status in statuses:
        exists = ApplicationStatus.query.filter_by(name=status).first()
        if not exists:
            db.session.add(ApplicationStatus(name=status))

    db.session.commit()
    print("Application statuses inserted successfully")
