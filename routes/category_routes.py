from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from extensions import db
from models.category import Category

category_bp = Blueprint(
    'categories',
    __name__,
    url_prefix='/admin/categories'
)

# -------------------------
# LIST
# -------------------------
# @category_bp.route('/')
# @login_required
# def list_categories():
#     if current_user.role.role_name != "Admin":
#         return "Access Denied", 403
#
#     categories = Category.query.order_by(Category.created_at.desc()).all()
#     return render_template('admin/categories/index.html', categories=categories)
@category_bp.route('/')
@login_required
def list_categories():
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    query = Category.query

    if search:
        query = query.filter(Category.name.ilike(f"%{search}%"))

    categories = query.order_by(
        Category.created_at.desc()
    ).paginate(page=page, per_page=10)

    return render_template(
        'admin/categories/index.html',
        categories=categories,
        search=search
    )
# -------------------------
# ADD
# -------------------------
@category_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_category():
    if current_user.role.role_name != "Admin":
        return "Access Denied", 403

    if request.method == 'POST':
        category = Category(
            name=request.form['name'],
            status=1
        )
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('categories.list_categories'))

    return render_template('admin/categories/add.html')

# -------------------------
# EDIT
# -------------------------
# @category_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
# def edit_category(id):
#     if current_user.role.role_name != "Admin":
#         return "Access Denied", 403
#
#     category = Category.query.get_or_404(id)
#
#     if request.method == 'POST':
#         category.name = request.form['name']
#         category.status = request.form.get('status', 1)
#         db.session.commit()
#         return redirect(url_for('categories.list_categories'))
#
#     return render_template('admin/categories/edit.html', category=category)

@category_bp.route('/get/<int:id>')
@login_required
def get_category(id):
    if current_user.role.role_name != "Admin":
        return {"error": "Unauthorized"}, 403

    category = Category.query.get_or_404(id)

    return {
        "id": category.id,
        "name": category.name,
        "status": category.status
    }