from app import db


class Venda(db.Model):
    __tablename__ = "vendas"

    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float, default=0)
    forma_pagamento = db.Column(db.String(30))
    criado_em = db.Column(db.DateTime, default=db.func.now())

    itens = db.relationship("ItemVenda", backref="venda", lazy=True, cascade="all, delete-orphan")