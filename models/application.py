"""
Модель отклика
Соответствует диаграмме классов модели:
- Отклик
  - id : int
  - статус : String
  - дата : Date
  - соискатель : Соискатель
  - вакансия : Вакансия
"""
from database import db
from datetime import datetime


class Application(db.Model):
    """
    Модель отклика соискателя на вакансию
    """
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)

    status = db.Column(db.String(20), default='pending')

    cover_letter = db.Column(db.Text)

    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vacancy_id = db.Column(db.Integer, db.ForeignKey('vacancies.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def update_status(self, new_status):
        """
        Метод обновитьСтатус(новыйСтатус : String) из диаграммы
        """
        valid_statuses = ['pending', 'accepted', 'rejected', 'invited']
        if new_status in valid_statuses:
            self.status = new_status
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    def __repr__(self):
        return f'<Application {self.id} - {self.status}>'