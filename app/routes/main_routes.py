from flask import Blueprint, render_template
from sqlalchemy import func
from datetime import date

from app.models.produto import Produto
from app.models.venda import Venda

main = Blueprint("main", __name__)


@main.route("/")
def home():
    hoje = date.today()

    vendas_hoje = Venda.query.filter(func.date(Venda.criado_em) == hoje).all()

    total_vendas = len(vendas_hoje)
    faturamento_hoje = sum(v.total or 0 for v in vendas_hoje)
    total_dinheiro = sum(v.total or 0 for v in vendas_hoje if v.forma_pagamento == "dinheiro")
    total_pix = sum(v.total or 0 for v in vendas_hoje if v.forma_pagamento == "pix")
    total_cartao = sum(v.total or 0 for v in vendas_hoje if v.forma_pagamento == "cartao")
    total_produtos = Produto.query.count()

    indicadores = {
        "vendas_hoje": total_vendas,
        "faturamento_hoje": faturamento_hoje,
        "peso_vendido_hoje": 0.00,
        "caixa_hoje": faturamento_hoje,
        "total_produtos": total_produtos,
        "dinheiro_hoje": total_dinheiro,
        "pix_hoje": total_pix,
        "cartao_hoje": total_cartao,
    }

    return render_template("index.html", indicadores=indicadores)