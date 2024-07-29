import datetime
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash, session, app
from flask_sqlalchemy import SQLAlchemy
from backend.models import db, Usuario, Inventario, Producto, Cocina
import os


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///datos_usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'clave_super_secreta'  # Clave secreta para sesiones



db.init_app(app)
with app.app_context():
    db.create_all()
    
def crear_productos():
    productos_para_cargar = [
        {'nombre': 'marroc', 'costo': 5, 'tiempo': 15},
        {'nombre': 'bananina', 'costo': 10, 'tiempo': 10},
        {'nombre': 'corazones', 'costo': 8, 'tiempo': 8},
        {'nombre': 'licorita', 'costo': 15, 'tiempo': 20}
    ]
    for producto_data in productos_para_cargar:
        producto = Producto(nombre=producto_data['nombre'], costo=producto_data['costo'], tiempo=producto_data['tiempo'])
        db.session.add(producto)

    db.session.commit()

def crear_cocinas(usuario_id):
    cocinas_cargar = [
        {'nombre': 'cocina1'},
        {'nombre': 'cocina2'},
        {'nombre': 'cocina3'}
    ]
    for cocina_data in cocinas_cargar:
        producto = Cocina(nombre=cocina_data['nombre'], usuario_id=usuario_id)
        db.session.add(producto)

    db.session.commit()


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form['email']
        nombre = request.form['nombre']
        contrasenia = request.form['contrasenia']

        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(email=email).first():
            flash('El usuario ya está registrado.', 'error')
            return redirect(url_for('registro'))

        # Crear nuevo usuario
        nuevo_usuario = Usuario(email=email, nombre=nombre, contrasenia=contrasenia)
        db.session.add(nuevo_usuario)
        db.session.commit()

        productos = Producto.query.all()
        if not productos:
            crear_productos()

        productos = Producto.query.all()
        for producto in productos:
            inventario = Inventario(usuario_id=nuevo_usuario.id, producto_id=producto.id, cantidad=0)
            db.session.add(inventario)

        crear_cocinas(nuevo_usuario.id)

        db.session.commit()

        flash('Registro exitoso. Por favor inicia sesión.', 'success')
        return redirect(url_for('index'))

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre = request.form['nombre']
        contrasenia = request.form['contrasenia']

        usuario = Usuario.query.filter_by(nombre=nombre, contrasenia=contrasenia).first()

        if usuario and usuario.contrasenia == contrasenia:
            session['usuario_id'] = usuario.id
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('pagina_usuario'))
        else:
            flash('Credenciales incorrectas. Inténtalo de nuevo.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash('Sesión cerrada exitosamente.', 'info')
    return redirect(url_for('index'))

@app.route('/usuario')
def pagina_usuario():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para ver esta página.', 'error')
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get(session['usuario_id'])
    inventarios = usuario.inventarios
    
    
    # Obtener los detalles de cada producto en el inventario del usuario
    productos = []
    for inventario in inventarios:
        producto = Producto.query.get(inventario.producto_id)
        productos.append({
            'nombre': producto.nombre,
            'cantidad': inventario.cantidad,
            'costo': producto.costo,
            'tiempo': producto.tiempo
        })


    cocinas = usuario.cocinas
    plata_usuario = usuario.plata
    

    usuario = Usuario.query.get(session['usuario_id'])
    return render_template('index.html', usuario=usuario, productos=productos, cocinas=cocinas, plata=plata_usuario)

@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    usuarios = Usuario.query.all()
    usuarios_json = [{'id': usuario.id, 'email': usuario.email, 'nombre': usuario.nombre, 'contrasenia': usuario.contrasenia} for usuario in usuarios]
    return jsonify(usuarios_json)

@app.route('/cocinar', methods=['POST'])
def cocinar():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'Debes iniciar sesión para cocinar.'})

    user_id = session['usuario_id']
    producto_id = request.form.get('producto_id')

    producto = Producto.query.get(producto_id)
    if not producto:
        return jsonify({'success': False, 'message': 'Producto no encontrado.'})

    inventario = Inventario.query.filter_by(usuario_id=user_id, producto_id=producto_id).first()
    if inventario:
        inventario.cantidad += 1
    else:
        inventario = Inventario(usuario_id=user_id, producto_id=producto_id, cantidad=1)
        db.session.add(inventario)

    db.session.commit()
    return jsonify({'success': True, 'message': f'Producto {producto.nombre} añadido al inventario.'})

@app.route('/misiones/<mision_id>', methods=['POST'])
def misiones(mision_id):
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'No estás autenticado.'})

    usuario_id = session['usuario_id']
    usuario = Usuario.query.get(usuario_id)
    
    # Define las misiones y sus requisitos
    misiones_requerimientos = {
        'mission1': {
            'productos': {
                1: 3,  # ID del producto y cantidad necesaria
                2: 2
            },
            'plata': 50
        },
        'mission2': {
            'productos': {
                3: 1,  # Ejemplo de otro producto y cantidad
                4: 2
            },
            'plata': 30
        },
        'mission3': {
            'productos': {
                1: 5,
                4: 1
            },
            'plata': 70
        },
        'mission4': {
            'productos': {
                2: 3,
                3: 4
            },
            'plata': 60
        }
    }
    
    if mision_id not in misiones_requerimientos:
        return jsonify({'success': False, 'message': 'Misión no encontrada.'})

    requisitos = misiones_requerimientos[mision_id]
    productos_requeridos = requisitos['productos']
    plata_ganada = requisitos['plata']

    # Verifica si el usuario tiene los productos necesarios
    for producto_id, cantidad_requerida in productos_requeridos.items():
        inventario = Inventario.query.filter_by(usuario_id=usuario_id, producto_id=producto_id).first()
        if not inventario or inventario.cantidad < cantidad_requerida:
            return jsonify({'success': False, 'message': 'No tienes los productos necesarios para esta misión.'})

    # Si tiene todos los productos necesarios, actualiza el inventario y añade plata
    for producto_id, cantidad_requerida in productos_requeridos.items():
        inventario = Inventario.query.filter_by(usuario_id=usuario_id, producto_id=producto_id).first()
        inventario.cantidad -= cantidad_requerida
        db.session.add(inventario)

    usuario.plata += plata_ganada
    db.session.commit()

    return jsonify({'success': True, 'message': f'Misión completada. Ganaste {plata_ganada} de plata.'})

if __name__ == '__main__':
    app.run(debug = True)