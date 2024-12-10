from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # Для роботи з часовими поясами

# Ініціалізація Flask додатку
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Параметри підключення до PostgreSQL
DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'Daniel+007',
    'host': 'localhost',
    'port': '5432'
}

# Функція для підключення до бази даних
def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

# Функція для отримання поточного часу з урахуванням часової зони України
def get_current_time():
    try:
        return datetime.now(ZoneInfo('Europe/Kyiv'))
    except ZoneInfoNotFoundError:
        return datetime.now()

# Головна сторінка: відображення всіх постів
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, image, date_posted FROM post ORDER BY date_posted DESC;")
    posts = cursor.fetchall()
    conn.close()

    # Перетворення даних у список словників
    formatted_posts = [
        {
            'id': row[0],
            'text': row[1],
            'image': row[2],
            'date_posted': row[3]
        }
        for row in posts
    ]
    return render_template('index.html', posts=formatted_posts)

# Маршрут для додавання нового поста
@app.route('/add', methods=['POST'])
def add_post():
    text = request.form.get('text')
    image = None

    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(image_path)
            image = os.path.join('static', 'uploads', file.filename)

    # Збереження даних у базу
    current_time = get_current_time()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO post (text, image, date_posted) VALUES (%s, %s, %s)",
        (text, image, current_time)
    )
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# Маршрут для видалення поста
@app.route('/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM post WHERE id = %s", (post_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Запуск додатку
if __name__ == '__main__':
    app.run(debug=True)
