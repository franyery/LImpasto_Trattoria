from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import Factura, DetalleFactura, Plato, Reservacion, Cliente, Categoria, Mesa
from datetime import datetime

# Blueprint sincronizado para el sistema L'Impasto
ventas_bp = Blueprint('ventas', __name__)

@ventas_bp.route("/menu", methods=["GET", "POST"])
def menu():
    if request.method == "POST":
        try:
            nombre = request.form.get('nombre')
            precio = request.form.get('precio')
            categoria_id = request.form.get('categoria_id')
            
            if nombre and precio and categoria_id:
                nuevo_plato = Plato(
                    nombre=nombre, 
                    precio=float(precio), 
                    categoria_id=int(categoria_id)
                )
                db.session.add(nuevo_plato)
                db.session.commit()
                flash(f"Plato '{nombre}' agregado correctamente", "success")
            else:
                flash("Faltan datos obligatorios para registrar el plato", "warning")
            return redirect(url_for('ventas.menu'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar plato: {e}", "danger")
            return redirect(url_for('ventas.menu'))

    return render_template("menu/list.html", 
                           platos=Plato.query.all(), 
                           categorias=Categoria.query.all())

# NUEVAS RUTAS PARA GESTIÓN COMPLETA DEL MENÚ
@ventas_bp.route("/menu/editar/<int:id>", methods=["POST"])
def editar_plato(id):
    try:
        p = Plato.query.get_or_404(id)
        p.nombre = request.form.get('nombre')
        p.precio = float(request.form.get('precio'))
        p.categoria_id = int(request.form.get('categoria_id'))
        db.session.commit()
        flash("Plato actualizado con éxito", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al editar: {e}", "danger")
    return redirect(url_for('ventas.menu'))

@ventas_bp.route("/menu/eliminar/<int:id>", methods=["POST"])
def eliminar_plato(id):
    try:
        p = Plato.query.get_or_404(id)
        db.session.delete(p)
        db.session.commit()
        flash("Plato eliminado del menú", "warning")
    except Exception as e:
        db.session.rollback()
        flash(f"No se puede eliminar: el plato tiene historial de ventas", "danger")
    return redirect(url_for('ventas.menu'))

@ventas_bp.route("/menu/categoria", methods=["POST"])
def nueva_categoria():
    try:
        nombre = request.form.get('nombre')
        if nombre:
            n = Categoria(nombre=nombre)
            db.session.add(n)
            db.session.commit()
            flash("Nueva categoría creada", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error: {e}", "danger")
    return redirect(url_for('ventas.menu'))

@ventas_bp.route("/facturar_directo", methods=["GET", "POST"])
def facturar_directo():
    if request.method == "POST":
        try:
            cid = request.form.get('cliente_id')
            res = Reservacion(
                fecha=datetime.now().strftime("%Y-%m-%d %H:%M"), 
                personas=0, 
                cliente_id=int(cid), 
                mesa_id=None
            )
            db.session.add(res)
            db.session.flush()

            p_ids = request.form.getlist('platos[]')
            cants = request.form.getlist('cantidades[]')
            
            return procesar_venta(res, p_ids, cants, es_local=False)
        except Exception as e:
            db.session.rollback()
            flash(f"Error en venta directa: {e}", "danger")
            
    return render_template("facturas/directa.html", 
                           clientes=Cliente.query.all(), 
                           menu=Plato.query.all())

@ventas_bp.route("/facturar/<int:res_id>", methods=["GET", "POST"])
def nueva_factura(res_id):
    reserva = Reservacion.query.get_or_404(res_id)
    if request.method == "POST":
        try:
            p_ids = request.form.getlist('platos[]')
            cants = request.form.getlist('cantidades[]')
            
            resultado = procesar_venta(reserva, p_ids, cants, es_local=True)
            
            if reserva.mesa:
                reserva.mesa.estatus = "Disponible"
                db.session.commit()
            return resultado
        except Exception as e:
            db.session.rollback()
            flash(f"Error al procesar factura: {e}", "danger")
            
    return render_template("facturas/form.html", 
                           reserva=reserva, 
                           menu=Plato.query.all())

def procesar_venta(reserva, p_ids, cants, es_local):
    subtotal = 0
    detalles_datos = []
    
    for i in range(len(p_ids)):
        raw_cant = cants[i] if cants[i] is not None else 0
        cantidad = int(raw_cant) if str(raw_cant).isdigit() else 0
        
        if cantidad > 0:
            plato = Plato.query.get(int(p_ids[i]))
            precio_unitario = plato.precio if (plato and plato.precio is not None) else 0.0
            
            monto_linea = precio_unitario * cantidad
            subtotal += monto_linea
            
            detalles_datos.append({
                'p': plato, 
                'q': cantidad, 
                'm': monto_linea,
                'precio': precio_unitario,
                'nombre': plato.nombre if plato else "Producto Desconocido"
            })

    if not detalles_datos:
        flash("Debe seleccionar al menos un producto con cantidad válida", "warning")
        return redirect(request.referrer)

    itbis = float(subtotal) * 0.18
    propina = (float(subtotal) * 0.10) if es_local else 0.0
    total_final = subtotal + itbis + propina

    f = Factura(
        reservacion_id=reserva.reservacion_id, 
        cliente_id=reserva.cliente_id, 
        fecha=datetime.now(),
        subtotal=subtotal, 
        impuesto=itbis,      
        propina_legal=propina, 
        total=total_final
    )
    db.session.add(f)
    db.session.flush()

    for d in detalles_datos:
        db.session.add(DetalleFactura(
            factura_id=f.factura_id, 
            plato_id=d['p'].plato_id if d['p'] else 0, 
            cantidad=d['q'], 
            precio_unitario=d['precio'], 
            descripcion=d['nombre'], 
            total_linea=d['m']
        ))

    db.session.commit()
    
    tipo_msg = "LOCAL (28% total)" if es_local else "PARA LLEVAR (18% ITBIS)"
    flash(f"Factura #{f.factura_id} generada con éxito como {tipo_msg}", "success")
    return redirect(url_for('ventas.historial'))

@ventas_bp.route("/historial")
def historial():
    todas = Factura.query.order_by(Factura.fecha.desc()).all()
    return render_template("facturas/list.html", facturas=todas)