from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models.produto import Produto

produtos = Blueprint("produtos", __name__, url_prefix="/produtos")


@produtos.route("/")
def listar_produtos():
    lista = Produto.query.order_by(Produto.id.desc()).all()
    return render_template("produtos/listar.html", produtos=lista)


@produtos.route("/novo", methods=["GET", "POST"])
def novo_produto():
    if request.method == "POST":
        nome = request.form.get("nome")
        codigo = request.form.get("codigo")
        tipo = request.form.get("tipo")
        preco = float(request.form.get("preco") or 0)
        estoque = float(request.form.get("estoque") or 0)

        produto = Produto(
            nome=nome,
            codigo=codigo,
            tipo=tipo,
            preco=preco,
            estoque=estoque
        )

        db.session.add(produto)
        db.session.commit()

        return redirect(url_for("produtos.listar_produtos"))

    return render_template("produtos/novo.html")


@produtos.route("/editar/<int:produto_id>", methods=["GET", "POST"])
def editar_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)

    if request.method == "POST":
        produto.nome = request.form.get("nome")
        produto.codigo = request.form.get("codigo")
        produto.tipo = request.form.get("tipo")
        produto.preco = float(request.form.get("preco") or 0)
        produto.estoque = float(request.form.get("estoque") or 0)

        db.session.commit()

        return redirect(url_for("produtos.listar_produtos"))

    return render_template("produtos/editar.html", produto=produto)