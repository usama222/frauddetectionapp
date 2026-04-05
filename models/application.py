from extensions import db

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    logo_path = db.Column(db.String(255))
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    download_link = db.Column(db.String(500))
    image = db.Column(db.String(255))
    avg_rating = db.Column(db.Float, default=0)
    fraud_status = db.Column(db.String(50), default='Pending')
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime)

    category = db.relationship('Category', backref='applications')
    admin = db.relationship('User', backref='added_apps')

    def __repr__(self):
        return f"<Application {self.name}>"
