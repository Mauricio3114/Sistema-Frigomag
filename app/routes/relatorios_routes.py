from datetime import datetime
from flask import Blueprint, render_template, request
from sqlalchemy import func
from app import db

from app.models.venda import Venda
from app.models.item_venda import ItemVenda
from app.models.produto import Produto
from app.models.despesa import Despesa

relatorios = Blueprint("relatorios", __name__, url_prefix="/relatorios")

@relatorios.route("/", methods=["GET"])
def relatorio_vendas():
    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")

    query = Venda.query

    if data_inicio:
        data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        query = query.filter(Venda.criado_em >= data_inicio)

    if data_fim:
        data_fim = datetime.strptime(data_fim, "%Y-%m-%d")
        query = query.filter(Venda.criado_em <= data_fim)

    vendas = query.order_by(Venda.id.desc()).all()

    total = sum(v.total or 0 for v in vendas)
    qtd_vendas = len(vendas)

    dinheiro = sum(v.total or 0 for v in vendas if v.forma_pagamento == "dinheiro")
    pix = sum(v.total or 0 for v in vendas if v.forma_pagamento == "pix")
    debito = sum(v.total or 0 for v in vendas if v.forma_pagamento == "debito")
    credito = sum(v.total or 0 for v in vendas if v.forma_pagamento == "credito")

    return render_template(
        "relatorios/index.html",
        vendas=vendas,
        total=total,
        qtd_vendas=qtd_vendas,
        dinheiro=dinheiro,
        pix=pix,
        debito=debito,
        credito=credito,
        data_inicio=request.args.get("data_inicio", ""),
        data_fim=request.args.get("data_fim", "")
    )


@relatorios.route("/produtos")
def produtos_mais_vendidos():
    ranking = (
        db.session.query(
            Produto.nome,
            func.sum(ItemVenda.quantidade).label("total_qtd"),
            func.sum(ItemVenda.subtotal).label("total_valor")
        )
        .join(Produto, Produto.id == ItemVenda.produto_id)
        .group_by(Produto.nome)
        .order_by(func.sum(ItemVenda.quantidade).desc())
        .all()
    )

    return render_template("relatorios/produtos.html", ranking=ranking)


@relatorios.route("/estoque-baixo")
def estoque_baixo():
    produtos = (
        Produto.query
        .filter(Produto.estoque <= 3)
        .order_by(Produto.estoque.asc())
        .all()
    )

    return render_template("relatorios/estoque_baixo.html", produtos=produtos)


@relatorios.route("/movimentacao")
def movimentacao():
    from datetime import datetime
    from flask import request

    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")

    query_vendas = Venda.query
    query_despesas = Despesa.query

    if data_inicio:
        data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
        query_vendas = query_vendas.filter(Venda.criado_em >= data_inicio)
        query_despesas = query_despesas.filter(Despesa.criado_em >= data_inicio)

    if data_fim:
        data_fim = datetime.strptime(data_fim, "%Y-%m-%d")
        query_vendas = query_vendas.filter(Venda.criado_em <= data_fim)
        query_despesas = query_despesas.filter(Despesa.criado_em <= data_fim)

    vendas = query_vendas.all()
    despesas = query_despesas.all()

    total_entrada = sum(v.total or 0 for v in vendas)
    total_saida = sum(d.valor or 0 for d in despesas)

    saldo = total_entrada - total_saida

    return render_template(
        "relatorios/movimentacao.html",
        total_entrada=total_entrada,
        total_saida=total_saida,
        saldo=saldo,
        data_inicio=request.args.get("data_inicio", ""),
        data_fim=request.args.get("data_fim", "")
    )