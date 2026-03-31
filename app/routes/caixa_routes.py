from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, make_response
from sqlalchemy import func

from app import db
from app.models.caixa_diario import CaixaDiario
from app.models.venda import Venda

caixa_diario = Blueprint("caixa_diario", __name__, url_prefix="/caixa-diario")


@caixa_diario.route("/")
def painel_caixa():
    hoje = date.today()
    caixa = CaixaDiario.query.filter_by(data=hoje).first()

    if not caixa:
        return redirect(url_for("caixa_diario.abrir_caixa"))

    if caixa.status == "aberto":
        return redirect(url_for("vendas.nova_venda"))

    return render_template("caixa_diario/index.html", caixa=caixa)


@caixa_diario.route("/abrir", methods=["GET", "POST"])
def abrir_caixa():
    hoje = date.today()
    caixa_existente = CaixaDiario.query.filter_by(data=hoje).first()

    if caixa_existente and caixa_existente.status == "aberto":
        return redirect(url_for("vendas.nova_venda"))

    if request.method == "POST":
        valor_abertura = float(request.form.get("valor_abertura") or 0)

        # se existir um caixa fechado no mesmo dia, reaproveita o registro
        if caixa_existente and caixa_existente.status == "fechado":
            caixa_existente.valor_abertura = valor_abertura
            caixa_existente.valor_fechamento = None
            caixa_existente.total_vendas = 0
            caixa_existente.total_dinheiro = 0
            caixa_existente.diferenca = 0
            caixa_existente.status = "aberto"
            db.session.commit()
        else:
            caixa = CaixaDiario(
                data=hoje,
                valor_abertura=valor_abertura,
                status="aberto"
            )
            db.session.add(caixa)
            db.session.commit()

        return redirect(url_for("caixa_diario.painel_caixa"))

    return render_template("caixa_diario/abrir.html")


@caixa_diario.route("/fechar", methods=["GET", "POST"])
def fechar_caixa():
    hoje = date.today()
    caixa = CaixaDiario.query.filter_by(data=hoje).first()

    if not caixa:
        return redirect(url_for("caixa_diario.abrir_caixa"))

    vendas_hoje = Venda.query.filter(func.date(Venda.criado_em) == hoje).all()
    total_vendas = sum(v.total or 0 for v in vendas_hoje)
    total_dinheiro = sum(v.total or 0 for v in vendas_hoje if v.forma_pagamento == "dinheiro")

    esperado = (caixa.valor_abertura or 0) + total_dinheiro

    if request.method == "POST":
        valor_fechamento = float(request.form.get("valor_fechamento") or 0)

        caixa.total_vendas = total_vendas
        caixa.total_dinheiro = total_dinheiro
        caixa.valor_fechamento = valor_fechamento
        caixa.diferenca = valor_fechamento - esperado
        caixa.status = "fechado"

        db.session.commit()

        return redirect(url_for("caixa_diario.detalhe_caixa", caixa_id=caixa.id))

    return render_template(
        "caixa_diario/fechar.html",
        caixa=caixa,
        total_vendas=total_vendas,
        total_dinheiro=total_dinheiro,
        esperado=esperado
    )


@caixa_diario.route("/historico")
def historico_caixa():
    caixas = CaixaDiario.query.order_by(CaixaDiario.data.desc()).all()
    return render_template("caixa_diario/historico.html", caixas=caixas)


@caixa_diario.route("/<int:caixa_id>")
def detalhe_caixa(caixa_id):
    caixa = CaixaDiario.query.get_or_404(caixa_id)
    return render_template("caixa_diario/detalhe.html", caixa=caixa)


@caixa_diario.route("/<int:caixa_id>/pdf")
def pdf_caixa(caixa_id):
    caixa = CaixaDiario.query.get_or_404(caixa_id)

    html = render_template("caixa_diario/pdf.html", caixa=caixa)
    response = make_response(html)
    response.headers["Content-Type"] = "text/html"

    return response