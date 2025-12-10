"""
Модель уведомлений
Используется в последовательности из sequence диаграммы
"""
from database import db
from datetime import datetime


class Notification(db.Model):
    """
    Модель уведомлений для пользователей
    """
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    notification_type = db.Column(db.String(50), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)

    related_id = db.Column(db.Integer)
    related_type = db.Column(db.String(50))

    is_read = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('notifications', lazy='dynamic'))

    def mark_as_read(self):
        """Отметить уведомление как прочитанное"""
        self.is_read = True
        db.session.commit()

    def __repr__(self):
        return f'<Notification {self.title}>'