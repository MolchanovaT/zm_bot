import asyncio
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

import config
from data.load_csv import load_data_from_csv  # Импортируем функцию с передачей пути

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Определяем директорию проекта
DATABASE_PATH = os.path.join(BASE_DIR, "data", "database.sqlite")  # Абсолютный путь

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = config.SECRET_KEY

db = SQLAlchemy(app)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class Dilers(db.Model):
    __tablename__ = "Dilers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    inn = db.Column(db.String(50), unique=True, nullable=False)
    allowed = db.Column(db.Boolean, default=True)


class LPU(db.Model):
    __tablename__ = "LPU"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    inn = db.Column(db.String(50), unique=True, nullable=False)
    allowed = db.Column(db.Boolean, default=True)


class PendingReview(db.Model):
    __tablename__ = "PendingReview"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    inn = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)
    denied = db.Column(db.Boolean, default=False)


login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("🚪 Вы вышли из системы!", "info")
    return redirect(url_for("login"))


@app.route('/')
@login_required
def index():
    dilers = Dilers.query.all()
    lpus = LPU.query.all()
    pending = PendingReview.query.all()
    return render_template('index.html', dilers=dilers, lpus=lpus, pending=pending, user=current_user)


@app.route('/toggle/<string:table>/<int:item_id>')
@login_required
def toggle_status(table, item_id):
    Model = Dilers if table == "Dilers" else LPU
    record = Model.query.get(item_id)
    if record:
        record.allowed = not record.allowed
        db.session.commit()
    return redirect(url_for('index'))


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_record():
    if request.method == "POST":
        name = request.form["name"]
        inn = request.form["inn"]
        table = request.form["table"]

        if table == "Dilers":
            new_record = Dilers(name=name, inn=inn)
        elif table == "LPU":
            new_record = LPU(name=name, inn=inn)
        elif table == "PendingReview":
            from datetime import datetime

            date_str = request.form.get("date")
            date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.today().date()
            approved = "approved" in request.form
            denied = "denied" in request.form

            new_record = PendingReview(name=name, inn=inn, date=date, approved=approved, denied=denied)
        else:
            flash("❌ Неизвестная таблица!", "danger")
            return redirect(url_for("index"))

        db.session.add(new_record)
        db.session.commit()
        flash(f"✅ Запись добавлена в {table}!", "success")
        return redirect(url_for("index"))

    return render_template("add.html")


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
    Model = {
        "Dilers": Dilers,
        "LPU": LPU,
        "PendingReview": PendingReview
    }.get(table)

    if not Model:
        flash("❌ Неверная таблица!", "danger")
        return redirect(url_for("index"))

    record = Model.query.get(item_id)
    if not record:
        flash("❌ Запись не найдена!", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        record.name = request.form["name"]
        record.inn = request.form["inn"]

        if table == "PendingReview":
            record.approved = "approved" in request.form
            record.denied = "denied" in request.form
            date_input = request.form.get("date")

            # Если запрет стоит, а дата не указана — ставим сегодняшнюю
            if record.denied and not date_input:
                record.date = datetime.today().date()
            else:
                try:
                    record.date = datetime.strptime(date_input, "%Y-%m-%d").date() if date_input else None
                except Exception:
                    record.date = None

        else:
            record.allowed = "allowed" in request.form

        db.session.commit()
        flash("✅ Запись обновлена!", "success")
        return redirect(url_for("index"))

    return render_template("edit.html", record=record, table=table)


@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    if "file" not in request.files:
        flash("❌ Файл не выбран!", "danger")
        return redirect(url_for("index"))

    file = request.files["file"]
    table = request.form["table"]

    if table == "PendingReview":
        model = PendingReview
    elif table == "Dilers":
        model = Dilers
    elif table == "LPU":
        model = LPU
    else:
        flash("❌ Неверная таблица!", "danger")
        return redirect(url_for("index"))

    if file.filename == "":
        flash("❌ Файл не выбран!", "danger")
        return redirect(url_for("index"))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(file_path)

        try:
            asyncio.run(load_data_from_csv(file_path, table, DATABASE_PATH))  # 🔑 передаём путь к БД
            flash(f"✅ Данные загружены в таблицу {table}!", "success")
        except Exception as e:
            flash(f"❌ Ошибка при загрузке файла: {str(e)}", "danger")

    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
