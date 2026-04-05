from app import create_app
from extensions import db
from models.role import Role
from models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # 1️⃣ Roles
    admin_role = Role(role_name="Admin")
    user_role = Role(role_name="User")

    db.session.add(admin_role)
    db.session.add(user_role)
    db.session.commit()

    print("Roles inserted")

    # 2️⃣ Admin User
    admin_user = User(
        name="Ahmed",
        email="admin@example.com",
        password=generate_password_hash("admin123"),
        role_id=admin_role.role_id
    )

    db.session.add(admin_user)
    db.session.commit()

    print("Admin user inserted")
