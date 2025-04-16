import os
from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import time


load_dotenv()

app = Flask(__name__)

db_config = {
    'host': 'mysql', 
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'pruvit123'),
    'database': os.getenv('DB_NAME', 'task_manager')
}

def create_connection():
    connection = None
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            connection = mysql.connector.connect(**db_config)
            print("Успішне підключення до MySQL")
            return connection
        except Error as e:
            retry_count += 1
            print(f"Спроба {retry_count}/{max_retries}: Помилка підключення до MySQL: {e}")
            
            if retry_count < max_retries:
                print(f"Повторна спроба через 5 секунд...")
                time.sleep(5)
            else:
                print("Максимальна кількість спроб вичерпана. Не вдалося підключитися до MySQL.")
    
    return connection

def init_db():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Створення таблиці, якщо вона не існує
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    status ENUM('new', 'in_progress', 'completed') DEFAULT 'new',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            connection.commit()
            print("База даних ініціалізована")
        except Error as e:
            print(f"Помилка ініціалізації бази даних: {e}")
        finally:
            cursor.close()
            connection.close()
    else:
        print("Ініціалізацію бази даних відкладено через відсутність підключення")
init_db()

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Заголовок завдання обов\'язковий'}), 400
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            query = "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s)"
            cursor.execute(query, (
                data['title'],
                data.get('description', ''),
                data.get('status', 'new')
            ))
            connection.commit()
            task_id = cursor.lastrowid
            return jsonify({'id': task_id, 'message': 'Завдання створено'}), 201
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    return jsonify({'error': 'Помилка підключення до бази даних'}), 500

@app.route('/tasks', methods=['GET'])
def get_all_tasks():
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM tasks")
            tasks = cursor.fetchall()
            return jsonify(tasks), 200
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    return jsonify({'error': 'Помилка підключення до бази даних'}), 500

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
            task = cursor.fetchone()
            if task:
                return jsonify(task), 200
            return jsonify({'error': 'Завдання не знайдено'}), 404
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    return jsonify({'error': 'Помилка підключення до бази даних'}), 500

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Дані не надані'}), 400
    
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Завдання не знайдено'}), 404
            
            query = "UPDATE tasks SET title = %s, description = %s, status = %s WHERE id = %s"
            cursor.execute(query, (
                data.get('title'),
                data.get('description'),
                data.get('status'),
                task_id
            ))
            connection.commit()
            return jsonify({'message': 'Завдання оновлено'}), 200
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    return jsonify({'error': 'Помилка підключення до бази даних'}), 500

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
            if not cursor.fetchone():
                return jsonify({'error': 'Завдання не знайдено'}), 404
            
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            connection.commit()
            return jsonify({'message': 'Завдання видалено'}), 200
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    return jsonify({'error': 'Помилка підключення до бази даних'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5001)), debug=True)