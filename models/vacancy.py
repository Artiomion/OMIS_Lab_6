"""
Модель вакансии
Соответствует диаграмме классов модели:
Вакансия
  - id : int
  - название : String
  - описание : String
  - требования : List<String>
  - работодатель : Работодатель
Методы:
- опубликовать()
- закрыть()
- Получить список требований()(ДОБАВИЛ)
"""
from database import db
from datetime import datetime


class Vacancy(db.Model):
    """
    Модель вакансии работодателя
    """
    __tablename__ = 'vacancies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text)
    salary = db.Column(db.String(100))
    location = db.Column(db.String(200))

    status = db.Column(db.String(20), default='draft')

    employer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    applications = db.relationship('Application', backref='vacancy', lazy='dynamic',
                                   cascade='all, delete-orphan')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def publish(self):
        """
        Метод опубликовать() из диаграммы классов
        """
        self.status = 'published'
        db.session.commit()

    def close(self):
        """
        Метод закрыть() из диаграммы классов
        """
        self.status = 'closed'
        db.session.commit()

    def get_requirements_list(self):
        """Получить список требований"""
        if self.requirements:
            return [r.strip() for r in self.requirements.split(',')]
        return []

    def __repr__(self):
        return f'<Vacancy {self.title}>'
