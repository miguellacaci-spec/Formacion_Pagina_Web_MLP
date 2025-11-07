from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///modo_carrera.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    position = db.Column(db.String(50), nullable=False)
    goals = db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html', title="Inicio")

@app.route('/modo_carrera', methods=['GET'])
def modo_carrera():
    players = Player.query.all()
    return render_template('modo_carrera.html', title="Modo Carrera", players=players)

@app.route('/add_player', methods=['POST'])
def add_player():
    try:
        name = request.form['name']
        age = int(request.form['age'])
        position = request.form['position']
        goals = int(request.form.get('goals', 0))
        new_player = Player(name=name, age=age, position=position, goals=goals)
        db.session.add(new_player)
        db.session.commit()
        return redirect('/modo_carrera')
    except Exception as e:
        return f"Error al agregar jugador: {e}"

@app.route('/partidos')
def partidos():
    return render_template('partidos.html', title="Partidos")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
