from extensions import db

class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Role {self.role_name}>"
