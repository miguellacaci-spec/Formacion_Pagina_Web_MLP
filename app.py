from flask import Flask, render_template, request, redirect, session
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash
# NOTA: Eliminamos la importación de init_db, ya que la lógica está ahora aquí.

app = Flask(__name__)
# ¡IMPORTANTE! Cambia esta clave secreta a algo largo y complejo antes de desplegar.
app.secret_key = "clave_super_segura_y_larga_para_la_session" 

# --- Función auxiliar para la conexión a la base de datos (AHORA CON CREACIÓN DE TABLAS) ---
def get_db_connection():
    # Conexión a la base de datos
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Creamos la tabla de Usuarios (si no existe)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # 2. Creamos la tabla de Jugadores (si no existe)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            position TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            nationality TEXT NOT NULL,
            grl INTEGER NOT NULL,
            market_value TEXT,
            salary TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    conn.commit()
    return conn

# --- Home ---
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    
    conn = get_db_connection()
    user = conn.execute("SELECT username FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()

    return render_template('home.html', username=user['username'] if user else 'Manager')

# --- Registro ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Seguridad: Hashing de la contraseña
        hashed_password = generate_password_hash(password)
        
        # Intentamos obtener la conexión y la tabla se crea si no existe
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            error = "❌ El nombre de usuario ya existe. Por favor, elige otro."
        except Exception as e:
            # Captura un error genérico, crucial para depurar el 500
            print(f"Error al registrar usuario: {e}") 
            error = "❌ Error interno del servidor al registrar. Inténtalo de nuevo."
        finally:
            conn.close()
        
        if not error and request.form.get('register') == 'true':
            # Solo redirigir si el registro fue exitoso y es la acción POST
            return redirect('/login')
            
    return render_template('register.html', error=error)

# --- Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        
        user = conn.execute("SELECT id, password FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect('/')
        else:
            error = "❌ Usuario o contraseña incorrectos"
            
    return render_template('login.html', error=error)

# --- Logout ---
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# --- Modo Carrera ---
@app.route('/modo_carrera', methods=['GET', 'POST'])
def modo_carrera():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    message = None 

    if request.method == 'POST':
        try:
            position = request.form['position']
            name = request.form['name']
            age = int(request.form['age'])
            nationality = request.form['nationality']
            grl = int(request.form['grl'])
            market_value = request.form['market_value']
            salary = request.form['salary']

            conn.execute('''
                INSERT INTO players (user_id, position, name, age, nationality, grl, market_value, salary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], position, name, age, nationality, grl, market_value, salary))
            conn.commit()
            message = "✅ Jugador añadido exitosamente."
        except ValueError:
            message = "⚠️ Error: La Edad y el GRL deben ser números enteros válidos."
        except Exception as e:
            message = f"❌ Error al añadir jugador: {str(e)}"
            print(f"Error adding player: {e}")


    # Obtiene los jugadores del usuario actual, ordenados por GRL
    players = conn.execute('SELECT * FROM players WHERE user_id=? ORDER BY grl DESC, name ASC', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('modo_carrera.html', players=players, message=message)

# --- Partidos ---
@app.route('/partidos')
def partidos():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('partidos.html')

# --- Ejecución Local / Producción ---
if __name__ == '__main__':
    # Solo para desarrollo local
    app.run(host='0.0.0.0', port=5000, debug=True)
