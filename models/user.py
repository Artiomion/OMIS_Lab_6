"""
Модель пользователя и её наследники
Соответствует диаграмме классов модели:
- Пользователь (базовый класс)
- Соискатель (наследник)
- Работодатель (наследник)
- Администратор (наследник)
"""
from database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    """
    Базовый класс пользователя
    Атрибуты из диаграммы:
    - id : int
    - имя : String
    - email : String
    - пароль : String
    - роль : String
    Методы:
    - войти()
    - выйти()(Реализован в auth_controller.py)
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_blocked = db.Column(db.Boolean, default=False)

    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        Метод войти() из диаграммы классов
        """
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.email}>'


class Applicant(User):
    """
    Соискатель (наследник User)
    Атрибуты из диаграммы:
    - списокРезюме : List<Резюме>
    Методы:
    - создатьРезюме()
    - откликнуться(вакансия)
    """
    __mapper_args__ = {
        'polymorphic_identity': 'applicant'
    }

    resumes = db.relationship('Resume', backref='applicant', lazy='dynamic',
                              foreign_keys='Resume.applicant_id',
                              cascade='all, delete-orphan')

    applications = db.relationship('Application', backref='applicant', lazy='dynamic',
                                   foreign_keys='Application.applicant_id',
                                   cascade='all, delete-orphan')

    def create_resume(self, title, experience, skills, education):
        """
        Метод создатьРезюме() из диаграммы классов
        """
        from models.resume import Resume
        resume = Resume(
            title=title,
            experience=experience,
            skills=skills,
            education=education,
            applicant_id=self.id
        )
        db.session.add(resume)
        db.session.commit()
        return resume

    def apply_to_vacancy(self, vacancy):
        """
        Метод откликнуться(вакансия) из диаграммы классов
        """
        from models.application import Application

        existing = Application.query.filter_by(
            applicant_id=self.id,
            vacancy_id=vacancy.id
        ).first()

        if existing:
            return None

        application = Application(
            applicant_id=self.id,
            vacancy_id=vacancy.id,
            status='pending'
        )
        db.session.add(application)
        db.session.commit()
        return application


class Employer(User):
    """
    Работодатель (наследник User)
    Атрибуты из диаграммы:
    - списокВакансий : List<Вакансия>
    Методы:
    - создатьВакансию()
    - просмотретьОтклики()
    """
    company_name = db.Column(db.String(200))
    company_description = db.Column(db.Text)

    __mapper_args__ = {
        'polymorphic_identity': 'employer'
    }

    vacancies = db.relationship('Vacancy', backref='employer', lazy='dynamic',
                                foreign_keys='Vacancy.employer_id',
                                cascade='all, delete-orphan')

    def create_vacancy(self, title, description, requirements, salary=None):
        """
        Метод создатьВакансию() из диаграммы классов
        """
        from models.vacancy import Vacancy
        vacancy = Vacancy(
            title=title,
            description=description,
            requirements=requirements,
            salary=salary,
            employer_id=self.id,
            status='draft'
        )
        db.session.add(vacancy)
        db.session.commit()
        return vacancy

    def view_applications(self):
        """
        Метод просмотретьОтклики() из диаграммы классов
        """
        from models.application import Application
        return Application.query.join(Application.vacancy).filter(
            Application.vacancy.has(employer_id=self.id)
        ).all()


class Administrator(User):
    """
    Администратор (наследник User)
    Методы:
    - модерироватьПользователя(пользователь)
    - просмотретьОтчёты()
    """
    __mapper_args__ = {
        'polymorphic_identity': 'administrator'
    }

    def moderate_user(self, user, block=True):
        """
        Метод модерироватьПользователя(пользователь) из диаграммы классов
        """
        user.is_blocked = block
        db.session.commit()

    def view_reports(self):
        """
        Метод просмотретьОтчёты() из диаграммы классов
        """
        from models.application import Application
        from models.vacancy import Vacancy
        from models.resume import Resume

        report = {
            'total_users': User.query.count(),
            'total_applicants': Applicant.query.count(),
            'total_employers': Employer.query.count(),
            'total_resumes': Resume.query.count(),
            'total_vacancies': Vacancy.query.count(),
            'total_applications': Application.query.count(),
            'blocked_users': User.query.filter_by(is_blocked=True).count()
        }
        return report
