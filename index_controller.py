from flask import Blueprint, render_template, request, redirect, url_for
from database import db
from models import Factura, DetalleFactura
from datetime import date, timedelta, datetime
from sqlalchemy import func, desc, cast, Date

home_bp = Blueprint('home', __name__)

@home_bp.route("/")
def index():
    return render_template("home.html")

# 1. Actualizamos la ruta para aceptar un parámetro opcional <mes>
@home_bp.route("/dashboard")
@home_bp.route("/dashboard/<int:mes>")
def dashboard(mes=None):
    try:
        hoy = date.today()
        anio_actual = hoy.year
        
        # 2. Determinamos qué mes visualizar (el seleccionado o el actual)
        if mes:
            mes_seleccionado = mes
        else:
            mes_seleccionado = hoy.month

        # 3. Calculamos el rango de fechas para el filtro SQL
        # Fecha inicio: día 1 del mes seleccionado
        fecha_inicio = date(anio_actual, mes_seleccionado, 1)
        
        # Fecha fin: día 1 del mes siguiente (para usar < fecha_fin)
        if mes_seleccionado == 12:
            fecha_fin = date(anio_actual + 1, 1, 1)
        else:
            fecha_fin = date(anio_actual, mes_seleccionado + 1, 1)

        # --- CONSULTAS ---

        # A. Total Hoy (Se mantiene fijo para monitoreo en tiempo real)
        total_hoy = db.session.query(func.sum(Factura.total)).filter(
            cast(Factura.fecha, Date) == hoy
        ).scalar() or 0
        
        # B. Total del Mes SELECCIONADO (Filtrado por rango de fechas)
        total_mes = db.session.query(func.sum(Factura.total)).filter(
            Factura.fecha >= fecha_inicio,
            Factura.fecha < fecha_fin
        ).scalar() or 0
        
        # C. Gráfica de Tendencia (Mantenemos últimos 7 días reales)
        labels, data_grafica = [], []
        for i in range(6, -1, -1):
            dia_busqueda = hoy - timedelta(days=i)
            labels.append(dia_busqueda.strftime("%a")) 
            venta_dia = db.session.query(func.sum(Factura.total)).filter(
                cast(Factura.fecha, Date) == dia_busqueda
            ).scalar() or 0
            data_grafica.append(float(venta_dia))

        # D. Top 5 Platos (¡Ahora filtrados por el mes seleccionado!)
        # Nota: Hacemos join con Factura para poder filtrar por fecha
        top_platos = db.session.query(
            DetalleFactura.descripcion, 
            func.sum(DetalleFactura.cantidad).label('total_vendido')
        ).join(Factura).filter(
            Factura.fecha >= fecha_inicio,
            Factura.fecha < fecha_fin
        ).group_by(DetalleFactura.descripcion)\
         .order_by(desc('total_vendido'))\
         .limit(5).all()

        # E. Proyección (Simulada para el mes visualizado)
        proyeccion = float(total_mes) * 1.15

        # --- DATOS PARA EL SELECTOR HTML ---
        nombres_meses = [
            (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
            (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
            (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
        ]

        return render_template("dashboard.html", 
                               labels=labels, 
                               data=data_grafica, 
                               total_mes=total_mes, 
                               total_hoy=total_hoy, 
                               top_platos=top_platos, 
                               proyeccion=proyeccion,
                               datetime_ahora=datetime.now().strftime("%d/%m/%Y %H:%M"),
                               # Nuevas variables enviadas a la vista
                               mes_actual=mes_seleccionado,
                               nombres_meses=nombres_meses)
    
    except Exception as e:
        print(f"DEBUG ERROR en Dashboard: {e}")
        # En caso de error, volvemos al dashboard sin filtro
        return redirect(url_for('home.dashboard'))
