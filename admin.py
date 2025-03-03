import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"csv"}

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Определяем директорию проекта
DATABASE_PATH = os.path.join(BASE_DIR, "data", "database.sqlite")  # Абсолютный путь

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "supersecretkey"

db = SQLAlchemy(app)

# Проверяем и создаём папку uploads при запуске
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


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


# Главная страница админки
@app.route('/')
def index():
    dilers = Dilers.query.all()
    lpus = LPU.query.all()
    return render_template('index.html', dilers=dilers, lpus=lpus)


# Обновление статуса "Разрешено/Запрещено"
@app.route('/toggle/<string:table>/<int:item_id>')
def toggle_status(table, item_id):
    if table == "Dilers":
        record = Dilers.query.get(item_id)
    elif table == "LPU":
        record = LPU.query.get(item_id)
    else:
        return "Ошибка: неверная таблица", 400

    if record:
        record.allowed = not record.allowed  # Инвертируем статус
        db.session.commit()
    return redirect(url_for('index'))


# Добавление записи
@app.route("/add", methods=["GET", "POST"])
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
def delete_record(table, item_id):
    if table == "Dilers":
        record = Dilers.query.get(item_id)
    elif table == "LPU":
        record = LPU.query.get(item_id)
    else:
        return "Ошибка: неверная таблица", 400

    if record:
        db.session.delete(record)
        db.session.commit()
    return redirect(url_for('index'))


@app.route("/edit/<string:table>/<int:item_id>", methods=["GET", "POST"])
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

        # ⬇️ Создаём папку uploads перед сохранением файла
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        file.save(file_path)

        # Загружаем данные из CSV в БД
        load_csv_to_db(file_path, table)
        flash(f"✅ Данные загружены в таблицу {table}!", "success")

    return redirect(url_for("index"))


# Очистка таблицы и загрузка новых данных
def load_csv_to_db(file_path, table):
    """Очищает таблицу и загружает данные из CSV"""
    df = pd.read_csv(file_path, encoding="windows-1251", dtype={"inn": str}, sep=",", quoting=3)

    df.dropna(subset=["inn"], inplace=True)  # Убираем пустые ИНН
    df["inn"] = df["inn"].astype(str)  # Приводим ИНН к строковому типу

    # **Удаляем дубликаты по ИНН, оставляя первую запись**
    df = df.drop_duplicates(subset=["inn"], keep="first")

    Model = Dilers if table == "Dilers" else LPU

    # Очищаем таблицу перед загрузкой новых данных
    db.session.query(Model).delete()
    db.session.commit()

    # Добавляем новые данные
    for _, row in df.iterrows():
        new_record = Model(name=row["name"], inn=row["inn"])
        db.session.add(new_record)

    db.session.commit()
    os.remove(file_path)  # Удаляем загруженный файл после обработки



# Запуск сервера
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
