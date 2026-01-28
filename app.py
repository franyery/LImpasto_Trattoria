from flask import Flask, render_template
from database import db
from controllers.index_controller import home_bp
from controllers.clientes_controller import clientes_bp
from controllers.mesas_controller import mesas_bp
from controllers.ventas_controller import ventas_bp
from datetime import datetime
from controllers.pedidos_controller import pedidos_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'limpasto_2026_trattoria'

    servidor = "WINIFER" 
    base_datos = "SISTEMA_DE_RESTAURANTE_TRATTORIA"

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mssql+pyodbc://@{servidor}/{base_datos}?"
        "driver=ODBC+Driver+17+for+SQL+Server&"
        "trusted_connection=yes&"
        "Encrypt=no&"
        "TrustServerCertificate=yes&"
        "Connect+Timeout=30"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Registro de Blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(mesas_bp, url_prefix='/reservacion')
    app.register_blueprint(ventas_bp, url_prefix='/ventas')
    app.register_blueprint(pedidos_bp)

    
    @app.context_processor
    def inject_vars():
        return {'datetime_ahora': datetime.now().strftime("%d/%m/%Y %H:%M")}

    return app

if __name__ == '__main__':
    app = create_app()
    
    app.run(debug=True)