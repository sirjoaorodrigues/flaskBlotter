from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin

app = Flask(__name__, static_folder='assets')

app.config['SECRET_KEY'] = 'PotatoSalad'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


class Operacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ativo = db.Column(db.String(20), nullable=False)
    fundo = db.Column(db.String(20), nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
    estrategia = db.Column(db.String(20), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    data = db.Column(db.String(10), nullable=False)
    user = db.Column(db.String(10), nullable=False)
