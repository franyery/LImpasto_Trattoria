from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import db
from models import Cliente

clientes_bp = Blueprint('clientes', __name__)

@clientes_bp.route("/clientes")
def index():
    q = request.args.get('q', '')
    if q:
        res = Cliente.query.filter(
            (Cliente.nombre.like(f"%{q}%")) |
            (Cliente.email.like(f"%{q}%")) |
            (Cliente.telefono.like(f"%{q}%"))
        ).all()
    else:
        res = Cliente.query.all()
    return render_template("clientes/list.html", clientes=res, busqueda=q)

@clientes_bp.route("/clientes/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        n = Cliente(
            nombre=request.form.get('nombre', '').strip(),
            telefono=request.form.get('telefono', '').strip(),
            email=request.form.get('email', '').strip()
        )
        db.session.add(n)
        db.session.commit()
        flash("Cliente registrado.", "success")
        return redirect(url_for('clientes.index'))
    return render_template("clientes/form.html")

@clientes_bp.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == "POST":
        cliente.nombre = request.form.get('nombre', '').strip()
        cliente.telefono = request.form.get('telefono', '').strip()
        cliente.email = request.form.get('email', '').strip()
        db.session.commit()
        flash("Cliente actualizado.", "success")
        return redirect(url_for('clientes.index'))
    return render_template("clientes/editar.html", cliente=cliente)

@clientes_bp.route("/clientes/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash("Cliente eliminado.", "warning")
    return redirect(url_for('clientes.index'))
