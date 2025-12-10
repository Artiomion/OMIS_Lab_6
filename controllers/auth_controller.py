"""
Контроллер аутентификации
Соответствует КонтроллерАутентификации из диаграммы классов контроллеров:
- войти(email : String, пароль : String) : Пользователь
- выйти(пользователь : Пользователь) : void
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash
from database import db
from models.user import User, Applicant, Employer, Administrator

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Реализует метод войти(email, пароль)
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        if not email or not password:
            flash('Пожалуйста, заполните все поля', 'error')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if user.is_blocked:
                flash('Ваш аккаунт заблокирован. Обратитесь к администратору.', 'error')
                return render_template('login.html')

            login_user(user, remember=remember)
            flash(f'Добро пожаловать, {user.name}!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            if user.role == 'applicant':
                return redirect(url_for('main.home'))
            elif user.role == 'employer':
                return redirect(url_for('main.employer_dashboard'))
            elif user.role == 'administrator':
                return redirect(url_for('admin.dashboard'))
        else:
            flash('Неверный email или пароль', 'error')

    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Регистрация нового пользователя
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        role = request.form.get('role', 'applicant')

        if not all([name, email, password, password_confirm]):
            flash('Пожалуйста, заполните все поля', 'error')
            return render_template('register.html')

        if password != password_confirm:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')

        if len(password) < 5:
            flash('Пароль должен содержать минимум 5 символов', 'error')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'error')
            return render_template('register.html')

        try:
            if role == 'applicant':
                user = Applicant(
                    name=name,
                    email=email,
                    password=generate_password_hash(password),
                    role='applicant'
                )
            elif role == 'employer':
                company_name = request.form.get('company_name', '')
                user = Employer(
                    name=name,
                    email=email,
                    password=generate_password_hash(password),
                    role='employer',
                    company_name=company_name
                )
            else:
                flash('Недопустимая роль пользователя', 'error')
                return render_template('register.html')

            db.session.add(user)
            db.session.commit()

            flash('Регистрация успешна! Теперь вы можете войти', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash('Ошибка при регистрации. Попробуйте снова.', 'error')
            print(f"Registration error: {e}")

    return render_template('register.html')


@auth_bp.route('/logout')
def logout():
    """
    Реализует метод выйти(пользователь)
    """
    logout_user()
    flash('Вы успешно вышли из системы', 'info')
    return redirect(url_for('auth.login'))