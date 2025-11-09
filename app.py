from flask import Flask, render_template, request, redirect, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "clave_super_segura"

# --- Función auxiliar ---
def get_db_connection():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Home ---
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('home.html')

# --- Registro ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "❌ Usuario ya existe."
        conn.close()
        return redirect('/login')
    return render_template('register.html')

# --- Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            return redirect('/')
        else:
            return "❌ Usuario o contraseña incorrectos"
    return render_template('login.html')

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

    if request.method == 'POST':
        position = request.form['position']
        name = request.form['name']
        age = request.form['age']
        nationality = request.form['nationality']
        grl = int(request.form['grl'])
        market_value = request.form['market_value']
        salary = request.form['salary']

        conn.execute('''
            INSERT INTO players (user_id, position, name, age, nationality, grl, market_value, salary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], position, name, age, nationality, grl, market_value, salary))
        conn.commit()

    players = conn.execute('SELECT * FROM players WHERE user_id=?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('modo_carrera.html', players=players)

# --- Partidos ---
@app.route('/partidos')
def partidos():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('partidos.html')

# --- Render fix ---
if __name__ == '__main__':
    if not os.path.exists('data.db'):
        import init_db
    app.run(host='0.0.0.0', port=5000)
