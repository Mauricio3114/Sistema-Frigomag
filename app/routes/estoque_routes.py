from flask import Blueprint, render_template, request, redirect, url_for
from app.models.produto import Produto
from app import db

# 👉 PRIMEIRO cria o blueprint
estoque = Blueprint("estoque", __name__, url_prefix="/estoque")


# 👉 depois usa ele nas rotas
@estoque.route("/")
def listar_estoque():
    produtos = Produto.query.order_by(Produto.nome.asc()).all()
    return render_template("estoque/listar.html", produtos=produtos)


@estoque.route("/ajustar/<int:produto_id>", methods=["GET", "POST"])
def ajustar_estoque(produto_id):
    produto = Produto.query.get_or_404(produto_id)

    if request.method == "POST":
        tipo = request.form.get("tipo")
        quantidade = float(request.form.get("quantidade") or 0)

        if quantidade > 0:
            if tipo == "entrada":
                produto.estoque += quantidade
            elif tipo == "saida":
                produto.estoque -= quantidade

            db.session.commit()

            return redirect(url_for("estoque.listar_estoque"))

    return render_template("estoque/ajustar.html", produto=produto)