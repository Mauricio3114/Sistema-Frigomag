from app import db


class CaixaDiario(db.Model):
    __tablename__ = "caixas_diarios"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False, unique=True)

    valor_abertura = db.Column(db.Float, default=0)
    valor_fechamento = db.Column(db.Float, nullable=True)

    total_vendas = db.Column(db.Float, default=0)
    total_dinheiro = db.Column(db.Float, default=0)

    diferenca = db.Column(db.Float, default=0)

    status = db.Column(db.String(20), default="aberto")  # aberto / fechado

    criado_em = db.Column(db.DateTime, default=db.func.now())