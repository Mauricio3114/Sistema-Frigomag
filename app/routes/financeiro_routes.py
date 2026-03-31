from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import func

from app import db
from app.models.despesa import Despesa
from app.models.venda import Venda

financeiro = Blueprint("financeiro", __name__, url_prefix="/financeiro")


@financeiro.route("/")
def dashboard_financeiro():
    hoje = date.today()

    vendas_hoje = Venda.query.filter(func.date(Venda.criado_em) == hoje).all()
    despesas_hoje = Despesa.query.filter(func.date(Despesa.criado_em) == hoje).all()

    faturamento_hoje = sum(v.total or 0 for v in vendas_hoje)
    dinheiro_hoje = sum(v.total or 0 for v in vendas_hoje if v.forma_pagamento == "dinheiro")
    pix_hoje = sum(v.total or 0 for v in vendas_hoje if v.forma_pagamento == "pix")
    debito_hoje = sum(v.total or 0 for v in vendas_hoje if v.forma_pagamento == "debito")
    credito_hoje = sum(v.total or 0 for v in vendas_hoje if v.forma_pagamento == "credito")

    total_despesas_hoje = sum(d.valor or 0 for d in despesas_hoje)
    lucro_hoje = faturamento_hoje - total_despesas_hoje

    return render_template(
        "financeiro/index.html",
        faturamento_hoje=faturamento_hoje,
        dinheiro_hoje=dinheiro_hoje,
        pix_hoje=pix_hoje,
        debito_hoje=debito_hoje,
        credito_hoje=credito_hoje,
        despesas_hoje=total_despesas_hoje,
        lucro_hoje=lucro_hoje,
        lista_despesas=despesas_hoje
    )


@financeiro.route("/nova-despesa", methods=["GET", "POST"])
def nova_despesa():
    if request.method == "POST":
        descricao = request.form.get("descricao")
        categoria = request.form.get("categoria")
        valor = request.form.get("valor")

        despesa = Despesa(
            descricao=descricao,
            categoria=categoria,
            valor=float(valor)
        )

        db.session.add(despesa)
        db.session.commit()

        return redirect(url_for("financeiro.dashboard_financeiro"))

    return render_template("financeiro/nova_despesa.html")