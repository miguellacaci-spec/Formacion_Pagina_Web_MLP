from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = "cuotadata_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///modo_carrera.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Orden de posiciones para organizar la tabla
POSITION_ORDER = ["POR", "LI", "CAI", "DFC", "LD", "CAD", "MCD", "MC", "MCO", "MI", "MD", "EI", "DC", "SD", "ED"]

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    nationality = db.Column(db.String(50), nullable=False)
    grl = db.Column(db.Integer, nullable=False)
    matches = db.Column(db.Integer, default=0)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    market_value = db.Column(db.Float, nullable=False)
    salary = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html', title="Inicio")

@app.route('/modo_carrera')
def modo_carrera():
    players = Player.query.all()
    # Ordenar jugadores según el orden de posiciones
    players.sort(key=lambda p: POSITION_ORDER.index(p.position) if p.position in POSITION_ORDER else 999)
    total_players = len(players)
    return render_template('modo_carrera.html', title="Modo Carrera", players=players, total_players=total_players)

@app.route('/add_player', methods=['POST'])
def add_player():
    try:
        name = request.form['name']
