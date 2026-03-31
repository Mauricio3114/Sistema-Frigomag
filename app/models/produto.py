from app import db


class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(120), nullable=False)
    codigo = db.Column(db.String(50), unique=True)

    tipo = db.Column(db.String(20))  # kg ou unidade

    preco = db.Column(db.Float, nullable=False)

    estoque = db.Column(db.Float, default=0)

    criado_em = db.Column(db.DateTime, default=db.func.now())