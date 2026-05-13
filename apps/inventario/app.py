from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 🔹 MODELOS
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    precio = db.Column(db.Float)

class HistorialPrecio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'))
    precio = db.Column(db.Float)
    fecha = db.Column(db.Date)
    producto = db.relationship('Producto', backref=db.backref('historial_precios', lazy=True))

# 🔹 CREAR DATOS DE PRUEBA
def crear_datos():
    db.create_all()

    if not Producto.query.first():
        producto = Producto(nombre="Tomate", precio=2500)
        db.session.add(producto)
        db.session.commit()

        # Generar 30 días de precios
        for i in range(30):
            fecha = (datetime.now() - timedelta(days=29 - i)).date()
            precio = random.randint(1800, 3000)

            registro = HistorialPrecio(
                producto_id=producto.id,
                precio=precio,
                fecha=fecha
            )
            db.session.add(registro)

        db.session.commit()

# Inicializar datos al arrancar
with app.app_context():
    crear_datos()

# 🔹 RUTA PRINCIPAL
@app.route('/')
def detalle():
    producto = Producto.query.first()
    if not producto:
        return render_template('detalle.html', producto=None, fechas=[], precios=[])

    fecha_limite = (datetime.now() - timedelta(days=30)).date()

    historial = HistorialPrecio.query.filter(
        HistorialPrecio.producto_id == producto.id,
        HistorialPrecio.fecha >= fecha_limite
    ).all()

    fechas = [h.fecha.strftime("%d-%m") for h in historial]
    precios = [h.precio for h in historial]

    return render_template(
        'detalle.html',
        producto=producto,
        fechas=fechas,
        precios=precios
    )

if __name__ == '__main__':
    app.run(debug=True)