from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

# --- CONFIGURACIÓN BÁSICA ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///futbol.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELOS DE DATOS ---
class Jugador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer)
    nacionalidad = db.Column(db.String(50))
    posicion = db.Column(db.String(50))
    grl = db.Column(db.Integer)
    goles = db.Column(db.Integer, default=0)
    asistencias = db.Column(db.Integer, default=0)
    valor_mercado = db.Column(db.Float)
    salario = db.Column(db.Float)

class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipo_local = db.Column(db.String(100))
    equipo_visitante = db.Column(db.String(100))
    fecha = db.Column(db.String(50))
    resultado = db.Column(db.String(20))
    cuota_local = db.Column(db.Float)
    cuota_empate = db.Column(db.Float)
    cuota_visitante = db.Column(db.Float)
    probabilidad_local = db.Column(db.Float)
    probabilidad_empate = db.Column(db.Float)
    probabilidad_visitante = db.Column(db.Float)

# --- CREAR LA BASE DE DATOS ---
# Evita el error de contexto usando app.app_context()
with app.app_context():
    if not os.path.exists("instance/futbol.db"):
        db.create_all()
        print("Base de datos creada correctamente ✅")

# --- RUTAS PRINCIPALES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/jugadores')
def jugadores():
    jugadores = Jugador.query.all()
    return render_template('jugadores.html', jugadores=jugadores)

@app.route('/partidos')
def partidos():
    partidos = Partido.query.all()
    return render_template('partidos.html', partidos=partidos)

@app.route('/api/jugadores', methods=['GET'])
def api_jugadores():
    jugadores = Jugador.query.all()
    data = [
        {
            "nombre": j.nombre,
            "edad": j.edad,
            "posicion": j.posicion,
            "goles": j.goles,
            "asistencias": j.asistencias
        }
        for j in jugadores
    ]
    return jsonify(data)

# --- PUNTO DE ENTRADA ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
