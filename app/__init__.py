from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    from app.routes.main_routes import main
    from app.routes.produto_routes import produtos
    from app.routes.venda_routes import vendas
    from app.routes.estoque_routes import estoque
    from app.routes.financeiro_routes import financeiro
    from app.routes.relatorios_routes import relatorios
    from app.routes.compras_routes import compras
    from app.routes.caixa_routes import caixa_diario

    app.register_blueprint(main)
    app.register_blueprint(produtos)
    app.register_blueprint(vendas)
    app.register_blueprint(estoque)
    app.register_blueprint(financeiro)
    app.register_blueprint(relatorios)
    app.register_blueprint(compras)
    app.register_blueprint(caixa_diario)

    with app.app_context():
        db.create_all()

    return app