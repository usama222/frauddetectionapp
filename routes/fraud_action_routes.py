from flask import Blueprint, redirect, url_for, request
from flask_login import login_required, current_user

from extensions import db
from models.application import Application
from models.fraud_detection_log import FraudDetectionLog

fraud_action_bp = Blueprint(
    'fraud_action',
    __name__,
    url_prefix='/admin/fraud-action'
)

# -------------------------
# APPROVE SUGGESTED STATUS
# -------------------------
@fraud_action_bp.route('/approve/<int:app_id>')
@login_required
def approve_suggested(app_id):
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    app = Application.query.get_or_404(app_id)
    log = FraudDetectionLog.query.filter_by(app_id=app_id).first_or_404()

    # Admin approves system suggestion
    app.fraud_status = log.suggested_status

    db.session.commit()
    return redirect(url_for('fraud_dashboard.dashboard'))


# -------------------------
# OVERRIDE STATUS MANUALLY
# -------------------------
@fraud_action_bp.route('/override/<int:app_id>', methods=['POST'])
@login_required
def override_status(app_id):
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    new_status = request.form.get('fraud_status')

    if new_status not in ['Genuine', 'Suspicious', 'Fraud']:
        return "Invalid status", 400

    app = Application.query.get_or_404(app_id)
    app.fraud_status = new_status

    db.session.commit()
    return redirect(url_for('fraud_dashboard.dashboard'))
