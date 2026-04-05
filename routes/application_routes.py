import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from extensions import db
from models.application import Application
from models.category import Category

application_bp = Blueprint(
    'applications',
    __name__,
    url_prefix='/admin/applications'
)

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------------------------------
# LIST (SEARCH + PAGINATION)
# -------------------------------------------------
@application_bp.route('/')
@login_required
def list_applications():
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    query = Application.query

    if search:
        query = query.filter(Application.name.ilike(f"%{search}%"))

    applications = query.order_by(
        Application.created_at.desc()
    ).paginate(page=page, per_page=10)

    return render_template(
        'admin/applications/index.html',
        applications=applications,
        search=search
    )


# -------------------------------------------------
# ADD APPLICATION (NEW PAGE + LOGO UPLOAD)
# -------------------------------------------------
@application_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_application():
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    categories = Category.query.filter_by(status=1).all()

    if request.method == 'POST':

        app = Application(
            name=request.form['name'],
            description=request.form['description'],
            category_id=request.form['category_id'],
            download_link=request.form['download_link'],
            fraud_status='Pending',
            added_by=current_user.id,
            created_at=datetime.utcnow(),
        )

        db.session.add(app)
        db.session.commit()

        # ---------- LOGO UPLOAD ----------
        file = request.files.get('logo')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()

            new_filename = f"app_{app.id}_{int(datetime.utcnow().timestamp())}.{ext}"
            upload_path = os.path.join(
                current_app.root_path,
                'static/admin/uploads/applications',
                new_filename
            )

            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            file.save(upload_path)

            app.logo_path = f"admin/uploads/applications/{new_filename}"
            db.session.commit()

        return redirect(url_for('applications.list_applications'))

    return render_template(
        'admin/applications/add.html',
        categories=categories
    )


# -------------------------------------------------
# EDIT APPLICATION (NEW PAGE + LOGO UPDATE)
# -------------------------------------------------
@application_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_application(id):
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    app_obj = Application.query.get_or_404(id)
    categories = Category.query.filter_by(status=1).all()

    if request.method == 'POST':

        app_obj.name = request.form['name']
        app_obj.description = request.form['description']
        app_obj.category_id = request.form['category_id']
        app_obj.download_link = request.form['download_link']
        app_obj.fraud_status = request.form['fraud_status']

        # ---------- LOGO UPDATE ----------
        file = request.files.get('logo')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()

            new_filename = f"app_{app_obj.id}_{int(datetime.utcnow().timestamp())}.{ext}"
            upload_path = os.path.join(
                current_app.root_path,
                'static/admin/uploads/applications',
                new_filename
            )

            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            file.save(upload_path)

            app_obj.logo_path = f"admin/uploads/applications/{new_filename}"

        db.session.commit()
        return redirect(url_for('applications.list_applications'))

    return render_template(
        'admin/applications/edit.html',
        app=app_obj,
        categories=categories
    )


# -------------------------------------------------
# DELETE APPLICATION
# -------------------------------------------------
@application_bp.route('/delete/<int:id>')
@login_required
def delete_application(id):
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    app_obj = Application.query.get_or_404(id)

    # (Optional) delete logo file later if you want
    db.session.delete(app_obj)
    db.session.commit()

    return redirect(url_for('applications.list_applications'))
