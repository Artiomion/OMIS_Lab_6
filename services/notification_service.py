"""
Сервис уведомлений
Соответствует СервисУведомлений из диаграммы классов инфраструктуры и NotificationController из sequence диаграммы
"""
from database import db
from models.notification import Notification


class NotificationService:
    """
    Методы:
    - Уведомить работодателя о новом отклике. Реализует функциональность из sequence диаграммы
    - Уведомить соискателя об изменении статуса отклика
    - Реализует notifyApplicant(invitation)(Уведомить соискателя о приглашении) из sequence диаграммы
    - Уведомить пользователя о блокировке
    """

    @staticmethod
    def send_notification(user, title, message, notification_type='system', related_id=None, related_type=None):
        """
        Отправить уведомление пользователю
        """
        notification = Notification(
            user_id=user.id,
            title=title,
            message=message,
            notification_type=notification_type,
            related_id=related_id,
            related_type=related_type
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def notify_application(employer, application):
        """
        Уведомить работодателя о новом отклике. Реализует функциональность из sequence диаграммы
        """
        title = 'Новый отклик на вакансию'
        message = f'Соискатель {application.applicant.name} откликнулся на вашу вакансию "{application.vacancy.title}"'

        return NotificationService.send_notification(
            user=employer,
            title=title,
            message=message,
            notification_type='application',
            related_id=application.id,
            related_type='application'
        )

    @staticmethod
    def notify_status_change(application):
        """
        Уведомить соискателя об изменении статуса отклика
        """
        status_messages = {
            'accepted': 'принят',
            'rejected': 'отклонен',
            'invited': 'вас пригласили на собеседование',
            'pending': 'находится на рассмотрении'
        }

        status_text = status_messages.get(application.status, application.status)
        title = 'Изменение статуса отклика'
        message = f'Ваш отклик на вакансию "{application.vacancy.title}" {status_text}'

        return NotificationService.send_notification(
            user=application.applicant,
            title=title,
            message=message,
            notification_type='application',
            related_id=application.id,
            related_type='application'
        )

    @staticmethod
    def notify_invitation(applicant, vacancy):
        """
        Реализует notifyApplicant(invitation)(Уведомить соискателя о приглашении) из sequence диаграммы
        """
        title = 'Приглашение от работодателя'
        message = f'Работодатель {vacancy.employer.name} приглашает вас рассмотреть вакансию "{vacancy.title}"'

        return NotificationService.send_notification(
            user=applicant,
            title=title,
            message=message,
            notification_type='invitation',
            related_id=vacancy.id,
            related_type='vacancy'
        )

    @staticmethod
    def notify_user_blocked(user):
        """
        Уведомить пользователя о блокировке
        """
        title = 'Ваш аккаунт заблокирован'
        message = 'Ваш аккаунт был заблокирован администратором. Для получения дополнительной информации обратитесь в поддержку.'

        return NotificationService.send_notification(
            user=user,
            title=title,
            message=message,
            notification_type='system'
        )
