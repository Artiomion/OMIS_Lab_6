# Платформа поиска работы

## Соответствие UML-диаграммам

### Диаграмма классов модели
- `User` - базовый класс пользователя [models/user.py](models/user.py)
- `Applicant` - соискатель (наследует User)
- `Employer` - работодатель (наследует User)
- `Administrator` - администратор (наследует User)
- `Resume` - резюме [models/resume.p](models/resume.py)
- `Vacancy` - вакансия [models/vacancy.py](models/vacancy.py)
- `Application` - отклик [models/application.py](models/application.py)


### Диаграмма классов контроллеров
- `КонтроллерАутентификации` → [auth_controller.py](controllers/auth_controller.py)
- `КонтроллерРезюме` → [resume_controller.py](controllers/resume_controller.py)
- `КонтроллерВакансий` → [vacancy_controller.py](controllers/vacancy_controller.py)
- `КонтроллерАдминистрирования` → [admin_controller.py](controllers/admin_controller.py)
- `КонтроллерКоммуникаций` → [notification_service.py](controllers/notification_service.py)

### Диаграмма классов инфраструктуры
- `БазаДанных` → [database.py](database.py)
- `РепозиторийПользователей` - реализован через SQLAlchemy ORM
- `РепозиторийРезюме` - реализован через SQLAlchemy ORM
- `РепозиторийВакансий` - реализован через SQLAlchemy ORM
- `СервисУведомлений` → [services/notification_service.py](services/notification_service.py)

### Диаграмма классов точки входа
- `Приложение` → [app.py](app.py) ([main()](app.py#L222), [create_app()](app.py#L226))
- `КонтейнерЗависимостей` - реализован через blueprints Flask

### Sequence диаграмма
Реализована функциональность:
- Поиск резюме работодателем [resume_controller.py::search()](`controllers/resume_controller.py#L181`)
- Просмотр резюме [resume_controller.py::view()](`controllers/resume_controller.py#L166`)
- Отправка приглашений/откликов
- Уведомления [notification_service.py](services/notification_service.py)
- Обновление статусов откликов

### Диаграмма состояний UI
Реализованы все состояния:
- UI_Вход → [login.html](templates/login.html)
- UI_ГлавноеМеню → [applicant_home.html](templates/applicant_home.html), [employer_dashboard.html](templates/employer_dashboard.html)
- UI_Вакансии → [vacancies.html](templates/vacancies.html)
- UI_СоздатьРезюме → [create_resume.html](templates/create_resume.html)
- UI_РедактированиеРезюме → [edit_resume.html](templates/edit_resume.html)
- UI_МоиРезюме → [my_resumes.html](templates/my_resumes.html)
- UI_Профиль → [profile.html](templates/profile.html)

## Архитектурные решения

### 1. Single Table Inheritance для пользователей
Используется паттерн Single Table Inheritance в SQLAlchemy для реализации иерархии User → Applicant/Employer/Administrator.

Это обеспечивает:
- Простоту запросов к БД
- Поддержку полиморфизма
- Эффективное хранение данных

### 2. MVC архитектура
- **Models** [models/](models/) - бизнес-логика и работа с данными
- **Views** [templates/](templates/) - представление (Jinja2 шаблоны)
- **Controllers** [controllers/](controllers/) - обработка запросов (Flask blueprints)

### 3. Repository паттерн
SQLAlchemy ORM выступает в роли репозиториев, предоставляя единый интерфейс для работы с данными.

### 4. Service слой
[NotificationService](services/notification_service.py#L10) инкапсулирует логику отправки уведомлений, обеспечивая разделение ответственности.

### Запуск приложения
```bash
python app.py
```

Приложение будет доступно по адресу: http://127.0.0.1:5000

### Тестовые аккаунты

При первом запуске автоматически создаются тестовые аккаунты:

**Соискатель:**
- Email: applicant@example.com
- Пароль: 12345

**Работодатель:**
- Email: employer@example.com
- Пароль: 12345

**Администратор:**
- Email: admin@example.com
- Пароль: admin123

## Структура проекта

```
job_platform/
├── app.py                          # Точка входа приложения
├── config.py                       # Конфигурация
├── database.py                     # Инициализация БД
├── models/                         # Модели данных
│   ├── __init__.py
│   ├── user.py                    # User, Applicant, Employer, Administrator
│   ├── resume.py                  # Resume
│   ├── vacancy.py                 # Vacancy
│   ├── application.py             # Application
│   └── notification.py            # Notification
├── controllers/                    # Контроллеры
│   ├── __init__.py
│   ├── auth_controller.py         # Контроллер Аутентификации
│   ├── resume_controller.py       # Контроллер Резюме
│   ├── vacancy_controller.py      # Контроллер Вакансий
│   └── admin_controller.py        # Контроллер Администрирования
├── services/                       # Сервисы
│   └── notification_service.py    # Контроллер Коммуникаций(Сервис уведомлений)
└── templates/                      # HTML шаблоны
    ├── base.html                  # Базовый шаблон
    ├── login.html                 # Вход
    ├── register.html              # Регистрация
    ├── applicant_home.html        # Главная соискателя
    ├── employer_dashboard.html    # Панель работодателя
    ├── my_resumes.html           # Список резюме
    ├── create_resume.html        # Создание резюме
    ├── edit_resume.html          # Редактирование резюме
    ├── view_resume.html          # Просмотр резюме
    ├── search_resumes.html       # Поиск резюме
    ├── vacancies.html            # Список вакансий
    ├── vacancy_detail.html       # Детали вакансии
    ├── my_vacancies.html         # Мои вакансии
    ├── create_vacancy.html       # Создание вакансии
    ├── edit_vacancy.html         # Редактирование вакансии
    ├── applications.html         # Отклики на вакансию
    ├── profile.html              # Профиль пользователя
    ├── notifications.html        # Уведомления
    ├── admin_dashboard.html      # Панель администратора
    ├── admin_users.html          # Управление пользователями
    ├── admin_reports.html        # Отчёты
    ├── 404.html                  # Страница ошибки 404
    └── 500.html                  # Страница ошибки 500
```

## Функциональность

### Для соискателей:
- Регистрация и вход в систему
- Создание и редактирование резюме
- Экспорт резюме в TXT и HTML форматы
- Поиск и просмотр вакансий
- Отклик на вакансии
- Отслеживание статусов откликов
- Получение уведомлений

### Для работодателей:
- Регистрация и вход в систему
- Создание и редактирование вакансий
- Публикация/закрытие вакансий
- Поиск резюме соискателей
- Просмотр откликов на вакансии
- Изменение статусов откликов
- Отправка приглашений соискателям

### Для администраторов:
- Просмотр статистики системы
- Управление пользователями
- Блокировка/разблокировка пользователей
- Удаление пользователей
- Просмотр детальных отчётов

## База данных

Используется SQLite с таблицами:
- `users` - пользователи (Single Table Inheritance)
- `resumes` - резюме
- `vacancies` - вакансии
- `applications` - отклики
- `notifications` - уведомления

## ошибки и отклонения от диаграмм

### Исправленные ошибки:
1. **Sequence диаграмма**: В диаграмме использовались классы `Invitation` и `InvitationController`, но в реализации используется модель `Application` со статусом "invited"
### Улучшения архитектуры:
1. Добавлена модель `Notification` для полноценной системы уведомлений
2. Добавлены метаданные `created_at`, `updated_at` для всех сущностей
3. Реализована пагинация для списков
4. Добавлена система сообщений для обратной связи с пользователем

## Стиль кодирования

- Используется PEP 8 для Python кода
- Комментарии соответствия UML диаграммам
- Разделение ответственности между слоями

## Безопасность

- Хеширование паролей с использованием Werkzeug
- Проверка прав доступа на уровне контроллеров
- Валидация пользовательского ввода

