"""
Главный файл приложения - точка входа
Соответствует диаграмме классов точки входа:
- Приложение (main(), инициализироватьСистему(), запуститьИнтерфейс())
- КонтейнерЗависимостей
"""
from flask import Flask, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from config import Config
from database import db, login_manager, init_db


def create_app(config_class=Config):
    """
    Реализует инициализироватьСистему() из диаграммы
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_db(app)

    from controllers.auth_controller import auth_bp
    from controllers.resume_controller import resume_bp
    from controllers.vacancy_controller import vacancy_bp
    from controllers.admin_controller import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(vacancy_bp)
    app.register_blueprint(admin_bp)

    register_main_routes(app)
    register_error_handlers(app)

    @app.context_processor
    def inject_notifications():
        """Добавляем уведомления в контекст всех шаблонов"""
        if current_user.is_authenticated:
            from models.notification import Notification
            unread_notifications = Notification.query.filter_by(
                user_id=current_user.id,
                is_read=False
            ).order_by(Notification.created_at.desc()).limit(5).all()
            unread_count = Notification.query.filter_by(
                user_id=current_user.id,
                is_read=False
            ).count()
            return dict(
                unread_notifications=unread_notifications,
                unread_count=unread_count
            )
        return dict(unread_notifications=[], unread_count=0)

    return app


def register_main_routes(app):

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('main.home'))
        return redirect(url_for('auth.login'))

    @app.route('/home')
    @login_required
    def home():
        if current_user.role == 'applicant':
            return redirect(url_for('main.applicant_home'))
        elif current_user.role == 'employer':
            return redirect(url_for('main.employer_dashboard'))
        elif current_user.role == 'administrator':
            return redirect(url_for('admin.dashboard'))
        return render_template('home.html')

    @app.route('/applicant/home')
    @login_required
    def applicant_home():
        if current_user.role != 'applicant':
            return redirect(url_for('main.home'))

        from models.resume import Resume
        from models.vacancy import Vacancy
        from models.application import Application

        resumes_count = Resume.query.filter_by(applicant_id=current_user.id).count()
        applications_count = Application.query.filter_by(applicant_id=current_user.id).count()

        recent_vacancies = Vacancy.query.filter_by(status='published').order_by(
            Vacancy.created_at.desc()
        ).limit(5).all()

        my_applications = Application.query.filter_by(applicant_id=current_user.id).order_by(
            Application.created_at.desc()
        ).limit(5).all()

        return render_template('applicant_home.html',
                               resumes_count=resumes_count,
                               applications_count=applications_count,
                               recent_vacancies=recent_vacancies,
                               my_applications=my_applications)

    @app.route('/employer/dashboard')
    @login_required
    def employer_dashboard():
        if current_user.role != 'employer':
            return redirect(url_for('main.home'))

        from models.vacancy import Vacancy
        from models.application import Application

        vacancies_count = Vacancy.query.filter_by(employer_id=current_user.id).count()
        published_count = Vacancy.query.filter_by(
            employer_id=current_user.id,
            status='published'
        ).count()

        applications_count = Application.query.join(Application.vacancy).filter(
            Application.vacancy.has(employer_id=current_user.id)
        ).count()

        pending_count = Application.query.join(Application.vacancy).filter(
            Application.vacancy.has(employer_id=current_user.id),
            Application.status == 'pending'
        ).count()

        my_vacancies = Vacancy.query.filter_by(employer_id=current_user.id).order_by(
            Vacancy.created_at.desc()
        ).limit(5).all()

        recent_applications = Application.query.join(Application.vacancy).filter(
            Application.vacancy.has(employer_id=current_user.id)
        ).order_by(Application.created_at.desc()).limit(5).all()

        return render_template('employer_dashboard.html',
                               vacancies_count=vacancies_count,
                               published_count=published_count,
                               applications_count=applications_count,
                               pending_count=pending_count,
                               my_vacancies=my_vacancies,
                               recent_applications=recent_applications)

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        """
        Соответствует состоянию UI_Профиль из диаграммы состояний
        """
        from flask import request, flash

        if request.method == 'POST':
            current_user.name = request.form.get('name')

            if current_user.role == 'employer':
                current_user.company_name = request.form.get('company_name')
                current_user.company_description = request.form.get('company_description')

            try:
                db.session.commit()
                flash('Профиль успешно обновлен!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Ошибка при обновлении профиля', 'error')
                print(f"Profile update error: {e}")

        return render_template('profile.html')

    @app.route('/notifications')
    @login_required
    def notifications():
        from models.notification import Notification

        page = request.args.get('page', 1, type=int)
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
            Notification.created_at.desc()
        ).paginate(page=page, per_page=20, error_out=False)

        return render_template('notifications.html', notifications=notifications)

    @app.route('/notifications/<int:notif_id>/read', methods=['POST'])
    @login_required
    def mark_notification_read(notif_id):
        from models.notification import Notification

        notification = Notification.query.get_or_404(notif_id)
        if notification.user_id == current_user.id:
            notification.mark_as_read()

        return redirect(url_for('main.notifications'))

    from flask import Blueprint
    main_bp = Blueprint('main', __name__)
    main_bp.add_url_rule('/home', 'home', home)
    main_bp.add_url_rule('/applicant/home', 'applicant_home', applicant_home)
    main_bp.add_url_rule('/employer/dashboard', 'employer_dashboard', employer_dashboard)
    main_bp.add_url_rule('/profile', 'profile', profile, methods=['GET', 'POST'])
    main_bp.add_url_rule('/notifications', 'notifications', notifications)
    main_bp.add_url_rule('/notifications/<int:notif_id>/read', 'mark_notification_read',
                         mark_notification_read, methods=['POST'])

    app.register_blueprint(main_bp)


def register_error_handlers(app):

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500


@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.query.get(int(user_id))


if __name__ == '__main__':
    """
    Реализует main() из диаграммы точки входа
    """
    app = create_app()

    print("=" * 60)
    print("Запущено на http://127.0.0.1:5000")
    print("Тестовые аккаунты:")
    print("Соискатель: applicant@example.com / 12345")
    print("Работодатель: employer@example.com / 12345")
    print("Администратор: admin@example.com / admin123")
    print("=" * 60)

    app.run(debug=True, host='127.0.0.1', port=5000)
