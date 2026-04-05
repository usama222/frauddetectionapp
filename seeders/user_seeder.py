from extensions import db
from models.user import User
from models.role import Role
from werkzeug.security import generate_password_hash

def seed_users():
    admin_role = Role.query.filter_by(role_name='Admin').first()
    user_role = Role.query.filter_by(role_name='User').first()

    users = [
        User(
            name="Ahmed Khan",
            email="ahmed@gmail.com",
            password=generate_password_hash("123456"),
            role_id=user_role.id,
            status=True
        ),
        User(
            name="Ali Raza",
            email="ali@gmail.com",
            password=generate_password_hash("123456"),
            role_id=user_role.id,
            status=False
        ),
        User(
            name="Sara Ahmed",
            email="sara@gmail.com",
            password=generate_password_hash("123456"),
            role_id=user_role.id,
            status=True
        ),
    ]

    db.session.bulk_save_objects(users)
    db.session.commit()

    print("Dummy users inserted")
