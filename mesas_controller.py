rom flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import Mesa, Reservacion, Cliente
from datetime import datetime

mesas_bp = Blueprint('reservacion', __name__)

@mesas_bp.route("/mesas", methods=["GET", "POST"])
def mesas():
    if request.method == "POST":
        nueva = Mesa(
            nombre=request.form['nombre'], 
            capacidad=int(request.form['capacidad']), 
            estatus="Disponible"
        )
        db.session.add(nueva)
        db.session.commit()
        flash("Mesa registrada con éxito", "success")
        return redirect(url_for('reservacion.mesas'))
    return render_template("mesas/list.html", mesas=Mesa.query.all())

@mesas_bp.route("/mesas/editar/<int:id>", methods=["POST"])
def editar_mesa(id):
    mesa = Mesa.query.get_or_404(id)
    mesa.nombre = request.form['nombre']
    mesa.capacidad = int(request.form['capacidad'])
    mesa.estatus = request.form['estatus']
    db.session.commit()
    flash(f"Mesa {mesa.nombre} actualizada", "info")
    return redirect(url_for('reservacion.mesas'))

@mesas_bp.route("/mesas/eliminar/<int:id>", methods=["POST"])
def eliminar_mesa(id):
    mesa = Mesa.query.get_or_404(id)
    db.session.delete(mesa)
    db.session.commit()
    flash("Mesa eliminada correctamente", "warning")
    return redirect(url_for('reservacion.mesas'))

@mesas_bp.route("/mesas/liberar/<int:id>", methods=["POST"])
def liberar_mesa(id):
    mesa = Mesa.query.get_or_404(id)
    mesa.estatus = "Disponible"
    db.session.commit()
    flash(f"La mesa {mesa.nombre} ahora está disponible", "success")
    return redirect(url_for('reservacion.mesas'))

@mesas_bp.route("/reservaciones")
def reservaciones(): 
    # Traemos las reservaciones ordenadas por fecha y hora
    todas = Reservacion.query.order_by(Reservacion.fecha.desc()).all()
    return render_template("reservaciones/list.html", reservaciones=todas)

@mesas_bp.route("/reservaciones/nueva", methods=["GET", "POST"])
def nueva_reservacion():
    if request.method == "POST":
        try:
            # Capturamos la fecha/hora y la mesa
            fecha_hora = request.form.get('fecha') # Formato: YYYY-MM-DDTHH:MM
            mesa_id = int(request.form['mesa_id'])
            mesa = Mesa.query.get_or_404(mesa_id)
            
            # Creamos la reserva
            res = Reservacion(
                fecha=fecha_hora.replace('T', ' '), # Limpiamos el formato para SQL Server
                personas=int(request.form['personas']), 
                cliente_id=int(request.form['cliente_id']), 
                mesa_id=mesa.mesa_id
            )
            mesa.estatus = "Ocupada" 
            
            db.session.add(res)
            db.session.commit()
            flash(f"Reservación confirmada para las {fecha_hora.split('T')[1]}", "success")
            return redirect(url_for('reservacion.reservaciones'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al procesar la reserva: {e}", "danger")
            return redirect(url_for('reservacion.nueva_reservacion'))
    
    # Manejo de selección previa desde la vista de mesas
    mesa_id_get = request.args.get('mesa_id')
    
    return render_template("reservaciones/form.html", 
                           clientes=Cliente.query.all(), 
                           mesas=Mesa.query.filter_by(estatus='Disponible').all(),
                           mesa_id_previa=mesa_id_get)

@mesas_bp.route("/reservaciones/eliminar/<int:id>", methods=["POST"])
def eliminar_reserva(id):
    res = Reservacion.query.get_or_404(id)
    # Liberación de la mesa asociada
    if res.mesa:
        res.mesa.estatus = "Disponible"
    db.session.delete(res)
    db.session.commit()
    flash("Reservación cancelada y mesa liberada", "warning")
    return redirect(url_for('reservacion.reservaciones'))
