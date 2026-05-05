from app import create_app
from extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    with db.engine.connect() as conn:
        # Add subject column if not exists
        try:
            conn.execute(text("ALTER TABLE feedback ADD COLUMN subject VARCHAR(255) NULL AFTER user_id"))
            print("Added: subject")
        except Exception as e:
            print(f"Skipped subject: {e}")

        # Add rating column if not exists
        try:
            conn.execute(text("ALTER TABLE feedback ADD COLUMN rating INT NULL AFTER message"))
            print("Added: rating")
        except Exception as e:
            print(f"Skipped rating: {e}")

        # Add ip_address column if not exists
        try:
            conn.execute(text("ALTER TABLE feedback ADD COLUMN ip_address VARCHAR(45) NULL AFTER rating"))
            print("Added: ip_address")
        except Exception as e:
            print(f"Skipped ip_address: {e}")

        conn.commit()
        print("Migration done.")
