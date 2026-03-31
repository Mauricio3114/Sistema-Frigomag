from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models.compra import Compra
from app.models.produto import Produto

compras = Blueprint("compras", __name__, url_prefix="/compras")


@compras.route("/")
def listar_compras():
    lista = Compra.query.order_by(Compra.id.desc()).all()
    return render_template("compras/listar.html", compras=lista)


@compras.route("/nova", methods=["GET", "POST"])
def nova_compra():
    produtos = Produto.query.order_by(Produto.nome.asc()).all()

    if request.method == "POST":
        fornecedor = request.form.get("fornecedor")
        produto_id = request.form.get("produto_id")
        quantidade = float(request.form.get("quantidade") or 0)
        custo_unitario = float(request.form.get("custo_unitario") or 0)
        observacao = request.form.get("observacao")

        produto = Produto.query.get(produto_id)

        if produto and quantidade > 0 and custo_unitario > 0:
            valor_total = quantidade * custo_unitario

            compra = Compra(
                fornecedor=fornecedor,
                produto_id=produto.id,
                quantidade=quantidade,
                custo_unitario=custo_unitario,
                valor_total=valor_total,
                observacao=observacao
            )

            db.session.add(compra)

            produto.estoque = float(produto.estoque or 0) + quantidade

            db.session.commit()

            return redirect(url_for("compras.listar_compras"))

    return render_template("compras/nova.html", produtos=produtos)