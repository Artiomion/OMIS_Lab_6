"""
Инициализация и управление базой данных
Соответствует диаграмме классов инфраструктуры (БазаДанных)
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def init_db(app):
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'

    with app.app_context():
        from models.user import User, Applicant, Employer, Administrator
        from models.resume import Resume
        from models.vacancy import Vacancy
        from models.application import Application
        from models.notification import Notification

        db.create_all()
        create_test_data()


def create_test_data():
    from models.user import User, Applicant, Employer, Administrator
    from models.resume import Resume
    from models.vacancy import Vacancy
    from werkzeug.security import generate_password_hash

    if User.query.first() is not None:
        return

    admin = Administrator(
        name='Администратор',
        email='admin@example.com',
        password=generate_password_hash('admin123'),
        role='administrator'
    )
    db.session.add(admin)

    applicant = Applicant(
        name='Артём Сотников',
        email='applicant@example.com',
        password=generate_password_hash('12345'),
        role='applicant'
    )
    db.session.add(applicant)

    employer = Employer(
        name='Петр Петров',
        email='employer@example.com',
        password=generate_password_hash('12345'),
        role='employer',
        company_name='EPAM Systems'
    )
    db.session.add(employer)

    employer2 = Employer(
        name='Иван Иванов',
        email='employer2@example.com',
        password=generate_password_hash('12345'),
        role='employer',
        company_name='Innowise'
    )
    db.session.add(employer2)

    db.session.commit()

    resume1 = Resume(
        title='Backend Developer',
        experience='опыт в разработке на Python',
        skills='HTML, Python, Flask',
        education='БГУИР, факультет ФИТУ',
        applicant_id=applicant.id
    )
    db.session.add(resume1)

    vacancy1 = Vacancy(
        title='Frontend Developer',
        description='Требуется опытный Frontend разработчик',
        requirements='React, TypeScript, 2+ года опыта',
        salary='1000-2000',
        employer_id=employer.id,
        status='published'
    )
    db.session.add(vacancy1)

    vacancy2 = Vacancy(
        title='Backend Developer',
        description='Ищем Backend разработчика в команду',
        requirements='Python, Django/Flask, PostgreSQL',
        salary='2000-3000',
        employer_id=employer.id,
        status='published'
    )
    db.session.add(vacancy2)

    vacancy3 = Vacancy(
        title='Frontend Developer (React)',
        description='Ищем сильного фронтендщика для разработки нового продукта с нуля',
        requirements='React, TypeScript, Redux Toolkit, REST/GraphQL, Figma',
        salary='2500-4000',
        employer_id=employer.id,
        status='published'
    )
    db.session.add(vacancy3)

    vacancy4 = Vacancy(
        title='Fullstack Python Developer',
        description='Нужен универсальный боец на поддержку и развитие нескольких сервисов',
        requirements='Python 3.11+, FastAPI, React/Vue, Docker, RabbitMQ/Celery',
        salary='3000-5000',
        employer_id=employer.id,
        status='published'
    )
    db.session.add(vacancy4)

    vacancy5 = Vacancy(
        title='DevOps Engineer',
        description='Расширяем инфраструктурную команду, ищем человека с боевым опытом',
        requirements='Kubernetes, Terraform, CI/CD (GitLab/GitHub Actions), Linux, Prometheus+Grafana',
        salary='3500-5500',
        employer_id=employer2.id,
        status='published'
    )
    db.session.add(vacancy5)

    vacancy6 = Vacancy(
        title='Mobile Developer (Flutter)',
        description='Ищем мобильщика под кросс-платформенную разработку новых приложений',
        requirements='Flutter 3+, Dart, Bloc/Cubit, Firebase, опыт публикации в stores',
        salary='2200-3800',
        employer_id=employer2.id,
        status='published'
    )
    db.session.add(vacancy6)

    vacancy7 = Vacancy(
        title='QA Automation Engineer',
        description='Нужен автоматизатор для покрытия веб и мобильных приложений тестами',
        requirements='Python/Java, Playwright/Selenium, Pytest, Appium, Allure',
        salary='1800-3200',
        employer_id=employer2.id,
        status='published'
    )
    db.session.add(vacancy7)

    vacancy8 = Vacancy(
        title='Senior Data Engineer',
        description='Строим DWH и пайплайны для аналитики и ML-команды',
        requirements='Python, Airflow, Spark, Snowflake/BigQuery, dbt, Kafka',
        salary='4000-7000',
        employer_id=employer.id,
        status='published'
    )
    db.session.add(vacancy8)

    db.session.commit()

    print("Соискатель: applicant@example.com / 12345")
    print("Работодатель: employer@example.com / 12345")
    print("Администратор: admin@example.com / admin123")