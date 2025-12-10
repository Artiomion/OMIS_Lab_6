"""
Контроллер вакансий
Соответствует КонтроллерВакансий из диаграммы классов контроллеров:
- создатьВакансию(работодатель : Работодатель) : Вакансия
- найтиВакансии(фильтр : String) : List<Вакансия>
- откликнуться(соискатель : Соискатель, вакансия : Вакансия) : void
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from database import db
from models.vacancy import Vacancy
from models.application import Application
from models.user import Employer, Applicant
from models.notification import Notification
from services.notification_service import NotificationService

vacancy_bp = Blueprint('vacancy', __name__, url_prefix='/vacancies')


@vacancy_bp.route('/')
@login_required
def list_vacancies():
    """
    Соответствует состоянию UI_Вакансии из диаграммы состояний
    Реализует метод найтиВакансии(фильтр)
    """
    query = request.args.get('q', '')
    vacancies = []

    if query:
        vacancies = Vacancy.query.filter(
            Vacancy.status == 'published',
            db.or_(
                Vacancy.title.ilike(f'%{query}%'),
                Vacancy.description.ilike(f'%{query}%'),
                Vacancy.requirements.ilike(f'%{query}%')
            )
        ).order_by(Vacancy.created_at.desc()).all()
    else:
        vacancies = Vacancy.query.filter_by(status='published').order_by(Vacancy.created_at.desc()).all()

    return render_template('vacancies.html', vacancies=vacancies, query=query)


@vacancy_bp.route('/<int:vacancy_id>')
@login_required
def view(vacancy_id):
    """
    Просмотр деталей вакансии
    """
    vacancy = Vacancy.query.get_or_404(vacancy_id)

    has_applied = False
    if current_user.role == 'applicant':
        has_applied = Application.query.filter_by(
            applicant_id=current_user.id,
            vacancy_id=vacancy_id
        ).first() is not None

    return render_template('vacancy_detail.html', vacancy=vacancy, has_applied=has_applied)


@vacancy_bp.route('/<int:vacancy_id>/apply', methods=['POST'])
@login_required
def apply(vacancy_id):
    """
    Реализует метод откликнуться(соискатель, вакансия)
    """
    if current_user.role != 'applicant':
        flash('Только соискатели могут откликаться на вакансии', 'error')
        return redirect(url_for('vacancy.list_vacancies'))

    vacancy = Vacancy.query.get_or_404(vacancy_id)

    if vacancy.status != 'published':
        flash('Эта вакансия недоступна для откликов', 'error')
        return redirect(url_for('vacancy.list_vacancies'))

    existing = Application.query.filter_by(
        applicant_id=current_user.id,
        vacancy_id=vacancy_id
    ).first()

    if existing:
        flash('Вы уже откликнулись на эту вакансию', 'warning')
        return redirect(url_for('vacancy.view', vacancy_id=vacancy_id))

    cover_letter = request.form.get('cover_letter', '')

    try:
        applicant = Applicant.query.get(current_user.id)
        application = applicant.apply_to_vacancy(vacancy)

        if application:
            application.cover_letter = cover_letter
            db.session.commit()

            NotificationService.notify_application(vacancy.employer, application)

            flash('Отклик успешно отправлен!', 'success')
        else:
            flash('Не удалось отправить отклик', 'error')

    except Exception as e:
        db.session.rollback()
        flash('Ошибка при отправке отклика', 'error')
        print(f"Application error: {e}")

    return redirect(url_for('vacancy.view', vacancy_id=vacancy_id))


@vacancy_bp.route('/my')
@login_required
def my_vacancies():
    """
    Мои вакансии (для работодателя)
    """
    if current_user.role != 'employer':
        flash('Только работодатели могут просматривать свои вакансии', 'error')
        return redirect(url_for('main.home'))

    vacancies = Vacancy.query.filter_by(employer_id=current_user.id).order_by(Vacancy.created_at.desc()).all()
    return render_template('my_vacancies.html', vacancies=vacancies)


@vacancy_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Реализует метод создатьВакансию(работодатель)
    """
    if current_user.role != 'employer':
        flash('Только работодатели могут создавать вакансии', 'error')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        salary = request.form.get('salary')
        location = request.form.get('location')

        if not all([title, description]):
            flash('Пожалуйста, заполните обязательные поля', 'error')
            return render_template('create_vacancy.html')

        try:
            employer = Employer.query.get(current_user.id)
            vacancy = employer.create_vacancy(
                title=title,
                description=description,
                requirements=requirements,
                salary=salary
            )
            vacancy.location = location
            db.session.commit()

            flash('Вакансия успешно создана!', 'success')
            return redirect(url_for('vacancy.my_vacancies'))

        except Exception as e:
            db.session.rollback()
            flash('Ошибка при создании вакансии', 'error')
            print(f"Vacancy creation error: {e}")

    return render_template('create_vacancy.html')


@vacancy_bp.route('/<int:vacancy_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(vacancy_id):
    """
    Редактировать вакансию
    """
    vacancy = Vacancy.query.get_or_404(vacancy_id)

    if vacancy.employer_id != current_user.id:
        flash('У вас нет прав для редактирования этой вакансии', 'error')
        return redirect(url_for('vacancy.my_vacancies'))

    if request.method == 'POST':
        vacancy.title = request.form.get('title')
        vacancy.description = request.form.get('description')
        vacancy.requirements = request.form.get('requirements')
        vacancy.salary = request.form.get('salary')
        vacancy.location = request.form.get('location')

        if not all([vacancy.title, vacancy.description]):
            flash('Пожалуйста, заполните обязательные поля', 'error')
            return render_template('edit_vacancy.html', vacancy=vacancy)

        try:
            db.session.commit()
            flash('Вакансия успешно обновлена!', 'success')
            return redirect(url_for('vacancy.my_vacancies'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении вакансии', 'error')
            print(f"Vacancy update error: {e}")

    return render_template('edit_vacancy.html', vacancy=vacancy)


@vacancy_bp.route('/<int:vacancy_id>/publish', methods=['POST'])
@login_required
def publish(vacancy_id):
    """
    Вызывает метод опубликовать() из модели Vacancy
    """
    vacancy = Vacancy.query.get_or_404(vacancy_id)

    if vacancy.employer_id != current_user.id:
        flash('У вас нет прав для публикации этой вакансии', 'error')
        return redirect(url_for('vacancy.my_vacancies'))

    vacancy.publish()
    flash('Вакансия опубликована!', 'success')
    return redirect(url_for('vacancy.my_vacancies'))


@vacancy_bp.route('/<int:vacancy_id>/close', methods=['POST'])
@login_required
def close(vacancy_id):
    """
    Вызывает метод закрыть() из модели Vacancy
    """
    vacancy = Vacancy.query.get_or_404(vacancy_id)

    if vacancy.employer_id != current_user.id:
        flash('У вас нет прав для закрытия этой вакансии', 'error')
        return redirect(url_for('vacancy.my_vacancies'))

    vacancy.close()
    flash('Вакансия закрыта!', 'success')
    return redirect(url_for('vacancy.my_vacancies'))


@vacancy_bp.route('/<int:vacancy_id>/delete', methods=['POST'])
@login_required
def delete(vacancy_id):
    """
    Удалить вакансию
    """
    vacancy = Vacancy.query.get_or_404(vacancy_id)

    if vacancy.employer_id != current_user.id:
        flash('У вас нет прав для удаления этой вакансии', 'error')
        return redirect(url_for('vacancy.my_vacancies'))

    try:
        db.session.delete(vacancy)
        db.session.commit()
        flash('Вакансия успешно удалена', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении вакансии', 'error')
        print(f"Vacancy deletion error: {e}")

    return redirect(url_for('vacancy.my_vacancies'))


@vacancy_bp.route('/<int:vacancy_id>/applications')
@login_required
def applications(vacancy_id):
    """
    Реализует функциональность просмотрf откликов на вакансию (view applications) из sequence диаграммы
    """
    vacancy = Vacancy.query.get_or_404(vacancy_id)

    if vacancy.employer_id != current_user.id:
        flash('У вас нет прав для просмотра откликов', 'error')
        return redirect(url_for('vacancy.my_vacancies'))

    applications = Application.query.filter_by(vacancy_id=vacancy_id).order_by(Application.created_at.desc()).all()
    return render_template('applications.html', vacancy=vacancy, applications=applications)


@vacancy_bp.route('/applications/<int:application_id>/status', methods=['POST'])
@login_required
def update_application_status(application_id):
    """
    Вызывает метод обновитьСтатус() из модели Application
    """
    application = Application.query.get_or_404(application_id)

    if application.vacancy.employer_id != current_user.id:
        flash('У вас нет прав для изменения статуса этого отклика', 'error')
        return redirect(url_for('main.home'))

    new_status = request.form.get('status')

    if application.update_status(new_status):
        # Отправляем уведомление соискателю
        NotificationService.notify_status_change(application)
        flash('Статус отклика обновлен!', 'success')
    else:
        flash('Недопустимый статус', 'error')

    return redirect(url_for('vacancy.applications', vacancy_id=application.vacancy_id))