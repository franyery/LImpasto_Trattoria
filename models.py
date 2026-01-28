from database import db
from datetime import datetime

class Cliente(db.Model):
    __tablename__ = "clientes"
    cliente_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(50))
    email = db.Column(db.String(120))
    reservas = db.relationship("Reservacion", backref="cliente", lazy=True)
    facturas = db.relationship("Factura", backref="cliente", lazy=True)

class Mesa(db.Model):
    __tablename__ = "mesas"
    mesa_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    estatus = db.Column(db.String(20), default="Disponible")
    reservas = db.relationship("Reservacion", backref="mesa", lazy=True)

class Categoria(db.Model):
    __tablename__ = "categorias"
    categoria_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    platos = db.relationship("Plato", backref="categoria", lazy=True)

class Plato(db.Model):
    __tablename__ = "Menu"
    plato_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False, default=0.0) # Protegido
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.categoria_id"), nullable=False)

class Reservacion(db.Model):
    __tablename__ = "reservaciones"
    reservacion_id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(20), nullable=False) 
    personas = db.Column(db.Integer, nullable=False, default=1)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.cliente_id"), nullable=False)
    mesa_id = db.Column(db.Integer, db.ForeignKey("mesas.mesa_id"), nullable=True)

class Factura(db.Model):
    __tablename__ = "facturas"
    factura_id = db.Column(db.Integer, primary_key=True)
    reservacion_id = db.Column(db.Integer, db.ForeignKey('reservaciones.reservacion_id'), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.cliente_id'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now) 
    
    # DESGLOSE DE LEY CON PROTECCIÓN CONTRA NULOS
    subtotal = db.Column(db.Float, default=0.0, nullable=False)
    impuesto = db.Column(db.Float, default=0.0, nullable=False)      # 18% ITBIS
    propina_legal = db.Column(db.Float, default=0.0, nullable=False) # 10% Local
    total = db.Column(db.Float, default=0.0, nullable=False)
    
    detalles = db.relationship("DetalleFactura", backref="factura", lazy=True)
    reservacion_rel = db.relationship("Reservacion", backref=db.backref("datos_factura", uselist=False))

class DetalleFactura(db.Model):
    __tablename__ = "detalle_factura"
    detalle_id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturas.factura_id'), nullable=False)
    plato_id = db.Column(db.Integer, db.ForeignKey('Menu.plato_id'), nullable=False)
    cantidad = db.Column(db.Integer, default=1, nullable=False)
    precio_unitario = db.Column(db.Float, default=0.0, nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    total_linea = db.Column(db.Float, default=0.0, nullable=False)
    plato = db.relationship("Plato")