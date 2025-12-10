"""
Контроллер администрирования
Соответствует КонтроллерАдминистрирования из диаграммы классов контроллеров:
- заблокироватьПользователя(id : int) : void
- сформироватьОтчёт() : void

Так же реализует методы из модели Administrator:
- просмотретьОтчёты()
- модерироватьПользователя()

- Удалить пользователя()(ДОБАВИЛ)
- Разблокировать пользователя()(ДОБАВИЛ)
- Удалить пользователя()(ДОБАВИЛ)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from database import db
from models.user import User, Administrator

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'administrator':
            flash('Требуются права администратора', 'error')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """
    Реализует метод просмотретьОтчёты() из модели Administrator
    """
    admin = Administrator.query.get(current_user.id)
    reports = admin.view_reports()

    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()

    return render_template('admin_dashboard.html', reports=reports, recent_users=recent_users)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """
    Реализует метод сформироватьОтчёт() - отчет по пользователям
    """
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')

    if search_query:
        users_pagination = User.query.filter(
            db.or_(
                User.name.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%')
            )
        ).paginate(page=page, per_page=20, error_out=False)
    else:
        users_pagination = User.query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )

    return render_template('admin_users.html', users=users_pagination, search_query=search_query)


@admin_bp.route('/users/<int:user_id>/block', methods=['POST'])
@login_required
@admin_required
def block_user(user_id):
    """
    Реализует метод заблокироватьПользователя(id) и модерироватьПользователя()
    """
    if user_id == current_user.id:
        flash('Вы не можете заблокировать себя', 'error')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(user_id)
    admin = Administrator.query.get(current_user.id)

    admin.moderate_user(user, block=True)

    flash(f'Пользователь {user.name} заблокирован', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/unblock', methods=['POST'])
@login_required
@admin_required
def unblock_user(user_id):
    """
    Разблокировать пользователя
    """
    user = User.query.get_or_404(user_id)
    admin = Administrator.query.get(current_user.id)

    admin.moderate_user(user, block=False)

    flash(f'Пользователь {user.name} разблокирован', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """
    Удалить пользователя
    """
    if user_id == current_user.id:
        flash('Вы не можете удалить себя', 'error')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(user_id)

    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'Пользователь {user.name} удален', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении пользователя', 'error')
        print(f"User deletion error: {e}")

    return redirect(url_for('admin.users'))


@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    """
    Реализует метод сформироватьОтчёт()
    """
    from models.resume import Resume
    from models.vacancy import Vacancy
    from models.application import Application
    from datetime import datetime, timedelta

    admin = Administrator.query.get(current_user.id)
    basic_reports = admin.view_reports()

    last_month = datetime.utcnow() - timedelta(days=30)

    detailed_reports = {
        'new_users_last_month': User.query.filter(User.created_at >= last_month).count(),
        'new_resumes_last_month': Resume.query.filter(Resume.created_at >= last_month).count(),
        'new_vacancies_last_month': Vacancy.query.filter(Vacancy.created_at >= last_month).count(),
        'new_applications_last_month': Application.query.filter(Application.created_at >= last_month).count(),
        'published_vacancies': Vacancy.query.filter_by(status='published').count(),
        'closed_vacancies': Vacancy.query.filter_by(status='closed').count(),
        'pending_applications': Application.query.filter_by(status='pending').count(),
    }

    return render_template('admin_reports.html',
                           basic_reports=basic_reports,
                           detailed_reports=detailed_reports)
