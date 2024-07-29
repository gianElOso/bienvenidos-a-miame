from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()   


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    contrasenia = db.Column(db.String(130), nullable=False)  
    plata = db.Column(db.Integer, default=100)
    inventarios = db.relationship('Inventario', backref='usuario', lazy=True)
    cocinas = db.relationship('Cocina', backref='usuario', lazy=True)

class Producto(db.Model):
    __tablename__ = 'producto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False) 
    costo = db.Column(db.Integer, nullable=False)
    tiempo = db.Column(db.Integer, nullable=False)

class Inventario(db.Model):
    __tablename__ = 'inventario'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=0)
    producto = db.relationship('Producto', backref='inventarios', lazy=True)

class Cocina(db.Model):
    __tablename__ = 'cocina'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    inicio = db.Column(db.DateTime, nullable=True)
    fin = db.Column(db.DateTime, nullable=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    producto = db.relationship('Producto', backref='cocinas', lazy=True)

