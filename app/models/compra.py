from app import db


class Compra(db.Model):
    __tablename__ = "compras"

    id = db.Column(db.Integer, primary_key=True)
    fornecedor = db.Column(db.String(150), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)

    quantidade = db.Column(db.Float, nullable=False)
    custo_unitario = db.Column(db.Float, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)

    observacao = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime, default=db.func.now())

    produto = db.relationship("Produto")