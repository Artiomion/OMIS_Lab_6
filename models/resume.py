"""
Модель резюме
Соответствует диаграмме классов модели:
Резюме
  - id : int
  - заголовок : String
  - опыт : String
  - навыки : List<String>
  - образование : String
Методы:
- экспортировать(формат : String)
"""
from database import db
from datetime import datetime


class Resume(db.Model):
    """
    Модель резюме соискателя
    """
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    experience = db.Column(db.Text)
    skills = db.Column(db.Text)
    education = db.Column(db.Text)
    additional_info = db.Column(db.Text)

    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def export(self, format_type='txt'):
        """
        Метод экспортировать(формат : String) из диаграммы
        """
        if format_type == 'txt':
            content = f"""
РЕЗЮМЕ: {self.title}

ОБРАЗОВАНИЕ:
{self.education or 'Не указано'}

ОПЫТ РАБОТЫ:
{self.experience or 'Не указан'}

НАВЫКИ:
{self.skills or 'Не указаны'}

ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:
{self.additional_info or 'Нет'}
            """
            return content.strip()

        elif format_type == 'html':
            content = f"""
            <html>
            <head><title>{self.title}</title></head>
            <body>
                <h1>{self.title}</h1>
                <h2>Образование</h2>
                <p>{self.education or 'Не указано'}</p>
                <h2>Опыт работы</h2>
                <p>{self.experience or 'Не указан'}</p>
                <h2>Навыки</h2>
                <p>{self.skills or 'Не указаны'}</p>
                <h2>Дополнительная информация</h2>
                <p>{self.additional_info or 'Нет'}</p>
            </body>
            </html>
            """
            return content

        return None

    def get_skills_list(self):
        """Получить список навыков"""
        if self.skills:
            return [s.strip() for s in self.skills.split(',')]
        return []

    def __repr__(self):
        return f'<Resume {self.title}>'
