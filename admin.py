import os
import pandas as pd
import asyncio
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

import config
from data.load_csv import load_data_from_csv  # Загружаем функцию импорта CSV

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Определяем директорию проекта
DATABASE_PATH = os.path.join(BASE_DIR, "data", "database.sqlite")  # Абсолютный путь

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = config.SECRET_KEY  # Берем секретный ключ из config

db = SQLAlchemy(app)

# Проверяем и создаём папку uploads при запуске
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Проверка формата файла
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Определяем модели для работы с БД
class Dilers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    inn = db.Column(db.String(50), unique=True, nullable=False)
    allowed = db.Column(db.Boolean, default=True)


class LPU(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    inn = db.Column(db.String(50), unique=True, nullable=False)
    allowed = db.Column(db.Boolean, default=True)


login_manager = LoginManager(app)
login_manager.login_view = "login"  # Если не авторизован — отправляет на страницу логина


# 👤 Модель пользователя (только админ)
class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


# 🔹 Страница логина
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == "admin" and password == config.PASSWORD:
            login_user(User(1))
            flash("✅ Вход выполнен!", "success")
            return redirect(url_for("index"))
        else:
            flash("❌ Неверный логин или пароль!", "danger")
    return render_template("login.html")


# 🔹 Выход из аккаунта
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("🚪 Вы вышли из системы!", "info")
    return redirect(url_for("login"))


# Главная страница админки
@app.route('/')
@login_required
def index():
    dilers = Dilers.query.all()
    lpus = LPU.query.all()
    return render_template('index.html', dilers=dilers, lpus=lpus, user=current_user)


# Обновление статуса "Разрешено/Запрещено"
@app.route('/toggle/<string:table>/<int:item_id>')
@login_required
def toggle_status(table, item_id):
    Model = Dilers if table == "Dilers" else LPU
    record = Model.query.get(item_id)
    if record:
        record.allowed = not record.allowed  # Инвертируем статус
        db.session.commit()
    return redirect(url_for('index'))


# Добавление записи
@app.route("/add", methods=["GET", "POST"])
@login_required
def add_record():
    """Добавление новой записи через веб-интерфейс"""
    if request.method == "POST":
        name = request.form["name"]
        inn = request.form["inn"]
        table = request.form["table"]

        Model = Dilers if table == "Dilers" else LPU
        new_record = Model(name=name, inn=inn)

        db.session.add(new_record)
        db.session.commit()

        flash(f"✅ Запись добавлена в {table}!", "success")
        return redirect(url_for("index"))

    return render_template("add.html")


# Удаление записи
@app.route('/delete/<string:table>/<int:item_id>')
@login_required
def delete_record(table, item_id):
    Model = Dilers if table == "Dilers" else LPU
    record = Model.query.get(item_id)
    if record:
        db.session.delete(record)
        db.session.commit()
    return redirect(url_for('index'))


@app.route("/edit/<string:table>/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_record(table, item_id):
    """Редактирование записи (название, ИНН, статус)"""
    Model = Dilers if table == "Dilers" else LPU
    record = Model.query.get(item_id)

    if not record:
        flash("❌ Запись не найдена!", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        record.name = request.form["name"]
        record.inn = request.form["inn"]
        record.allowed = "allowed" in request.form  # Получаем статус (чекбокс)

        db.session.commit()
        flash("✅ Запись обновлена!", "success")
        return redirect(url_for("index"))

    return render_template("edit.html", record=record, table=table)


# Загрузка CSV
@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    """Обрабатывает загрузку файла CSV"""
    if "file" not in request.files:
        flash("❌ Файл не выбран!", "danger")
        return redirect(url_for("index"))

    file = request.files["file"]
    table = request.form["table"]

    if file.filename == "":
        flash("❌ Файл не выбран!", "danger")
        return redirect(url_for("index"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        file.save(file_path)

        try:
            asyncio.run(load_data_from_csv(file_path, table))
            flash(f"✅ Данные загружены в таблицу {table}!", "success")
        except Exception as e:
            flash(f"❌ Ошибка при загрузке файла: {str(e)}", "danger")

    return redirect(url_for("index"))


# Запуск сервера
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
