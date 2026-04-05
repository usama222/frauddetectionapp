from flask import Flask
from config import Config
from extensions import db
from flask_login import LoginManager
from flask import request, redirect, url_for

# login_manager = LoginManager()
# login_manager.login_view = 'auth.admin_login'

# login_manager = LoginManager()
# login_manager.login_view = 'user_auth.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    #Define LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'user_auth.login'

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith('/admin'):
            return redirect(url_for('auth.admin_login'))
        return redirect(url_for('user_auth.login'))

    # Import models
    from models.user import User
    from models.role import Role
    from models.category import Category
    from models.application import Application
    from models.application_status import ApplicationStatus
    from models.sentiment_result import SentimentResult
    from models.review import Review
    from models.fraud_detection_log import FraudDetectionLog


    # USER LOADER
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # REGISTER BLUEPRINTS Admin
    from routes.application_routes import application_bp
    from routes.auth_routes import auth_bp
    from routes.category_routes import category_bp
    from routes.user_routes import user_bp
    from routes.feedback_routes import feedback_bp
    from routes.review_routes import review_bp
    from routes.admin_review_routes import admin_review_bp
    from routes.fraud_dashboard_routes import fraud_dashboard_bp
    from routes.fraud_action_routes import fraud_action_bp

    # REGISTER BLUEPRINT User
    from routes.user_auth_routes import user_auth_bp
    from routes.user_panel_routes import user_panel_bp


    app.register_blueprint(application_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(admin_review_bp)
    app.register_blueprint(fraud_dashboard_bp)
    app.register_blueprint(fraud_action_bp)

    # REGISTER BLUEPRINT User
    app.register_blueprint(user_auth_bp)
    app.register_blueprint(user_panel_bp)

    @app.route('/')
    def home():
        from flask_login import current_user
        if current_user.is_authenticated:
            if getattr(current_user.role, 'role_name', None) == "User":
                return redirect(url_for('user_panel.dashboard'))
            if getattr(current_user.role, 'role_name', None) == "Admin":
                return redirect(url_for('fraud_dashboard.dashboard'))
        return redirect(url_for('user_auth.login'))

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
