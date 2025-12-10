"""
Контроллер резюме
Соответствует КонтроллерРезюме из диаграммы классов контроллеров:
- создатьРезюме(соискатель : Соискатель) : Резюме
- редактировать(резюме : Резюме) : void
- экспортировать(резюме : Резюме, формат : String) : File

- Показать список резюме текущего пользователя (Соответствует состоянию UI_МоиРезюме из диаграммы состояний)
- Поиск резюме (Реализует функциональность из sequence диаграммы: searchResumes(criteria))

- Удалить резюме(ДОБАВИЛ)
- Просмотр резюме (для работодателей)(ДОБАВИЛ)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, make_response
from flask_login import login_required, current_user
from database import db
from models.resume import Resume
from models.user import Applicant

resume_bp = Blueprint('resume', __name__, url_prefix='/resumes')


@resume_bp.route('/')
@login_required
def my_resumes():
    """
    Показать список резюме текущего пользователя
    Соответствует состоянию UI_МоиРезюме из диаграммы состояний
    """
    if current_user.role != 'applicant':
        flash('Только соискатели могут просматривать резюме', 'error')
        return redirect(url_for('main.home'))

    resumes = Resume.query.filter_by(applicant_id=current_user.id).order_by(Resume.created_at.desc()).all()
    return render_template('my_resumes.html', resumes=resumes)


@resume_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Реализует метод создатьРезюме(соискатель)
    Соответствует состоянию UI_СоздатьРезюме из диаграммы состояний
    """
    if current_user.role != 'applicant':
        flash('Только соискатели могут создавать резюме', 'error')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        education = request.form.get('education')
        experience = request.form.get('experience')
        skills = request.form.get('skills')
        additional_info = request.form.get('additional_info')

        if not title:
            flash('Пожалуйста, укажите заголовок резюме', 'error')
            return render_template('create_resume.html')

        try:
            applicant = Applicant.query.get(current_user.id)
            resume = applicant.create_resume(
                title=title,
                experience=experience,
                skills=skills,
                education=education
            )
            resume.additional_info = additional_info
            db.session.commit()

            flash('Резюме успешно создано!', 'success')
            return redirect(url_for('resume.my_resumes'))

        except Exception as e:
            db.session.rollback()
            flash('Ошибка при создании резюме', 'error')
            print(f"Resume creation error: {e}")

    return render_template('create_resume.html')


@resume_bp.route('/<int:resume_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(resume_id):
    """
    Реализует метод редактировать(резюме)
    Соответствует состоянию UI_РедактированиеРезюме из диаграммы состояний
    """
    resume = Resume.query.get_or_404(resume_id)

    if resume.applicant_id != current_user.id:
        flash('У вас нет прав для редактирования этого резюме', 'error')
        return redirect(url_for('resume.my_resumes'))

    if request.method == 'POST':
        resume.title = request.form.get('title')
        resume.education = request.form.get('education')
        resume.experience = request.form.get('experience')
        resume.skills = request.form.get('skills')
        resume.additional_info = request.form.get('additional_info')

        if not resume.title:
            flash('Пожалуйста, укажите заголовок резюме', 'error')
            return render_template('edit_resume.html', resume=resume)

        try:
            db.session.commit()
            flash('Резюме успешно обновлено!', 'success')
            return redirect(url_for('resume.my_resumes'))
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при обновлении резюме', 'error')
            print(f"Resume update error: {e}")

    return render_template('edit_resume.html', resume=resume)


@resume_bp.route('/<int:resume_id>/delete', methods=['POST'])
@login_required
def delete(resume_id):
    """
    Удалить резюме
    """
    resume = Resume.query.get_or_404(resume_id)

    if resume.applicant_id != current_user.id:
        flash('У вас нет прав для удаления этого резюме', 'error')
        return redirect(url_for('resume.my_resumes'))

    try:
        db.session.delete(resume)
        db.session.commit()
        flash('Резюме успешно удалено', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при удалении резюме', 'error')
        print(f"Resume deletion error: {e}")

    return redirect(url_for('resume.my_resumes'))


@resume_bp.route('/<int:resume_id>/export')
@login_required
def export(resume_id):
    """
    Реализует метод экспортировать(резюме, формат)
    """
    resume = Resume.query.get_or_404(resume_id)

    if resume.applicant_id != current_user.id and current_user.role != 'employer':
        flash('У вас нет прав для экспорта этого резюме', 'error')
        return redirect(url_for('main.home'))

    format_type = request.args.get('format', 'txt')

    content = resume.export(format_type)

    if content:
        response = make_response(content)
        if format_type == 'txt':
            response.headers['Content-Type'] = 'text/plain; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=resume_{resume_id}.txt'
        elif format_type == 'html':
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            response.headers['Content-Disposition'] = f'attachment; filename=resume_{resume_id}.html'
        return response

    flash('Неподдерживаемый формат экспорта', 'error')
    return redirect(url_for('resume.my_resumes'))


@resume_bp.route('/<int:resume_id>/view')
@login_required
def view(resume_id):
    """
    Просмотр резюме (для работодателей)
    """
    resume = Resume.query.get_or_404(resume_id)

    if current_user.role == 'applicant' and resume.applicant_id != current_user.id:
        flash('У вас нет прав для просмотра этого резюме', 'error')
        return redirect(url_for('resume.my_resumes'))

    return render_template('view_resume.html', resume=resume)


@resume_bp.route('/search')
@login_required
def search():
    """
    Реализует функциональность из sequence диаграммы: searchResumes(criteria)
    """
    if current_user.role != 'employer':
        flash('Только работодатели могут искать резюме', 'error')
        return redirect(url_for('main.home'))

    query = request.args.get('q', '')
    resumes = []

    if query:
        resumes = Resume.query.filter(
            db.or_(
                Resume.title.ilike(f'%{query}%'),
                Resume.skills.ilike(f'%{query}%'),
                Resume.experience.ilike(f'%{query}%')
            )
        ).all()
    else:
        resumes = Resume.query.order_by(Resume.created_at.desc()).limit(50).all()

    return render_template('search_resumes.html', resumes=resumes, query=query)
