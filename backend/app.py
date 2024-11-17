# backend/app.py

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_mysqldb import MySQL
import os
from flask import Flask, render_template

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')  # Usa la variable de entorno SECRET_KEY o una clave por defecto

# Configuración de conexión a MySQL desde variables de entorno
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '1234')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'todo_db')

mysql = MySQL(app)

# Diccionario de traducciones
translations = {
    'es': {
        'title': 'Lista de Tareas',
        'add_task': 'Agregar',
        'completed_tasks': 'Tareas Completadas',
        'pending_tasks': 'Tareas Pendientes',
        'archived_tasks': 'Tareas Archivadas',
        'delete_task': 'Eliminar',
        'login': 'Iniciar sesión',
        'username': 'Nombre de usuario',
        'password': 'Contraseña',
        'login_failed': 'Nombre de usuario o contraseña inválidos',
        'tags_placeholder': 'Etiquetas (entre comas)',
        'filter_by_tag': 'Filtrar por etiqueta',
        'filter': 'Filtrar',
        'task_name': 'Nombre de la tarea',
        'logout': 'Cerrar sesión',
    }
}

def get_translation():
    return translations.get('es')  # Retorna siempre en español

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', texts=get_translation())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and user[2] == password:
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', texts=get_translation(), error=get_translation()['login_failed'])

    return render_template('login.html', texts=get_translation())

@app.route('/todos', methods=['GET'])
def get_todos():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT t.id, t.task, t.completed, t.archived, GROUP_CONCAT(tag.name) AS tags
            FROM todos t
            LEFT JOIN task_tags tt ON t.id = tt.task_id
            LEFT JOIN tags tag ON tt.tag_id = tag.id
            GROUP BY t.id
        """)
        tasks = cur.fetchall()
        cur.close()

        todos = [
            {"id": task[0], "task": task[1], "completed": bool(task[2]), "archived": bool(task[3]), "tags": task[4].split(',') if task[4] else []}
            for task in tasks
        ]
        
        return jsonify({
            'pending': [todo for todo in todos if not todo['completed'] and not todo['archived']],
            'completed': [todo for todo in todos if todo['completed'] and not todo['archived']],
            'archived': [todo for todo in todos if todo['archived']]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/todos/<int:id>/archive', methods=['PUT'])
def toggle_archive_task(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT archived FROM todos WHERE id = %s", (id,))
        task = cur.fetchone()

        if not task:
            return jsonify({"error": "Task not found"}), 404

        new_archived_state = not task[0]
        cur.execute("UPDATE todos SET archived = %s WHERE id = %s", (new_archived_state, id))
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Task archive state updated!", "archived": new_archived_state})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/todos/<int:id>/complete', methods=['PUT'])
def toggle_complete_todo(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT completed FROM todos WHERE id = %s", (id,))
        task = cur.fetchone()

        if not task:
            return jsonify({"error": "Task not found"}), 404

        new_state = not task[0]
        cur.execute("UPDATE todos SET completed = %s WHERE id = %s", (new_state, id))
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Task state updated!", "completed": new_state})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/todos', methods=['POST'])
def add_todo():
    try:
        new_task = request.json.get('task')
        tags = request.json.get('tags', [])

        if not new_task:
            return jsonify({"error": "Task cannot be empty"}), 400
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO todos (task, completed) VALUES (%s, %s)", (new_task, False))
        mysql.connection.commit()
        task_id = cur.lastrowid
        
        for tag_name in tags:
            cur.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
            tag = cur.fetchone()
            if tag:
                tag_id = tag[0]
                cur.execute("INSERT INTO task_tags (task_id, tag_id) VALUES (%s, %s)", (task_id, tag_id))
            else:
                cur.execute("INSERT INTO tags (name) VALUES (%s)", (tag_name,))
                mysql.connection.commit()
                tag_id = cur.lastrowid
                cur.execute("INSERT INTO task_tags (task_id, tag_id) VALUES (%s, %s)", (task_id, tag_id))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({"message": "Task added!", "task": new_task, "tags": tags}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/todos/<int:id>/tags', methods=['POST'])
def add_tag_to_task(id):
    try:
        tag_name = request.json.get('tag')
        if not tag_name:
            return jsonify({"error": "Tag cannot be empty"}), 400
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
        tag = cur.fetchone()
        
        if not tag:
            cur.execute("INSERT INTO tags (name) VALUES (%s)", (tag_name,))
            mysql.connection.commit()
            tag_id = cur.lastrowid
        else:
            tag_id = tag[0]
        
        cur.execute("INSERT INTO task_tags (task_id, tag_id) VALUES (%s, %s)", (id, tag_id))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({"message": "Tag added to task!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/todos/filter', methods=['GET'])
def filter_tasks_by_tag():
    try:
        tag_name = request.args.get('tag')
        if not tag_name:
            return jsonify({"error": "Tag parameter is required"}), 400
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
        tag = cur.fetchone()
        
        if not tag:
            return jsonify({"error": "Tag not found"}), 404
        
        tag_id = tag[0]
        cur.execute("""
            SELECT todos.id, todos.task, todos.completed 
            FROM todos
            JOIN task_tags ON todos.id = task_tags.task_id
            WHERE task_tags.tag_id = %s
        """, (tag_id,))
        tasks = cur.fetchall()
        cur.close()
        
        tasks_data = [{"id": task[0], "task": task[1], "completed": task[2]} for task in tasks]
        return jsonify({"tasks": tasks_data})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/todos/<int:id>', methods=['PUT'])
def edit_todo(id):
    try:
        updated_task = request.json.get('task')
        updated_tags = request.json.get('tags', [])

        if not updated_task:
            return jsonify({"error": "Task cannot be empty"}), 400

        cur = mysql.connection.cursor()
        cur.execute("UPDATE todos SET task = %s WHERE id = %s", (updated_task, id))
        mysql.connection.commit()

        cur.execute("DELETE FROM task_tags WHERE task_id = %s", (id,))
        mysql.connection.commit()

        for tag_name in updated_tags:
            cur.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
            tag = cur.fetchone()
            if tag:
                tag_id = tag[0]
                cur.execute("INSERT INTO task_tags (task_id, tag_id) VALUES (%s, %s)", (id, tag_id))
            else:
                cur.execute("INSERT INTO tags (name) VALUES (%s)", (tag_name,))
                mysql.connection.commit()
                tag_id = cur.lastrowid
                cur.execute("INSERT INTO task_tags (task_id, tag_id) VALUES (%s, %s)", (id, tag_id))
        
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Task updated!", "task": updated_task, "tags": updated_tags})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
