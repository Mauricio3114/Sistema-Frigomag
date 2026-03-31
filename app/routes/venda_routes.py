from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for, session

from app import db
from app.models.caixa_diario import CaixaDiario
from app.models.item_venda import ItemVenda
from app.models.produto import Produto
from app.models.venda import Venda
from app.utils.datetime_utils import agora

vendas = Blueprint("vendas", __name__, url_prefix="/vendas")


@vendas.route("/", methods=["GET", "POST"])
def nova_venda():
    hoje = date.today()
    caixa = CaixaDiario.query.filter_by(data=hoje).first()

    if not caixa or caixa.status != "aberto":
        return redirect("/caixa-diario/abrir")

    produtos = Produto.query.order_by(Produto.nome.asc()).all()

    if "carrinho" not in session:
        session["carrinho"] = []

    carrinho = session["carrinho"]

    if request.method == "POST":
        acao = request.form.get("acao")

        if acao == "add":
            produto_id = request.form.get("produto_id")
            codigo = request.form.get("codigo", "").strip()
            quantidade_texto = (request.form.get("quantidade") or "").strip()
            quantidade = float(quantidade_texto) if quantidade_texto else 1

            produto = None

            if codigo:
                codigo_numerico = "".join(filter(str.isdigit, codigo))

                # etiqueta real da balança:
                # 2 + 6 dígitos do produto + 5 dígitos do valor + 1 dígito verificador
                if codigo_numerico.startswith("2") and len(codigo_numerico) >= 12:
                    cod_produto = codigo_numerico[1:7]
                    valor_centavos = codigo_numerico[7:12]

                    produto = Produto.query.filter_by(codigo=cod_produto).first()

                    if produto:
                        valor = float(valor_centavos) / 100

                        carrinho.append({
                            "produto_id": produto.id,
                            "nome": produto.nome,
                            "quantidade": 1,
                            "preco": valor,
                            "subtotal": valor
                        })

                        session["carrinho"] = carrinho
                        return redirect(url_for("vendas.nova_venda"))

                # código simples do produto
                produto = Produto.query.filter_by(codigo=codigo_numerico).first()

            # fallback por select
            if not produto and produto_id:
                produto = Produto.query.get(produto_id)

            # venda normal por quantidade/peso
            if produto and quantidade > 0:
                subtotal = produto.preco * quantidade

                carrinho.append({
                    "produto_id": produto.id,
                    "nome": produto.nome,
                    "quantidade": quantidade,
                    "preco": produto.preco,
                    "subtotal": subtotal
                })

                session["carrinho"] = carrinho

                return redirect(url_for("vendas.nova_venda"))

        elif acao == "remover":
            index = int(request.form.get("index"))
            if 0 <= index < len(carrinho):
                carrinho.pop(index)
                session["carrinho"] = carrinho

        elif acao == "limpar":
            session["carrinho"] = []

        elif acao == "finalizar":
            forma_pagamento = request.form.get("forma_pagamento")

            if carrinho:
                total = sum(item["subtotal"] for item in carrinho)

                venda = Venda(
                    total=total,
                    forma_pagamento=forma_pagamento,
                    criado_em=agora()
                )
                db.session.add(venda)
                db.session.flush()

                for item in carrinho:
                    item_db = ItemVenda(
                        venda_id=venda.id,
                        produto_id=item["produto_id"],
                        quantidade=item["quantidade"],
                        preco_unitario=item["preco"],
                        subtotal=item["subtotal"]
                    )
                    db.session.add(item_db)

                    produto = Produto.query.get(item["produto_id"])
                    if produto:
                        produto.estoque -= item["quantidade"]

                db.session.commit()

                session["carrinho"] = []

                return redirect(url_for("vendas.cupom_venda", venda_id=venda.id))

    total = sum(item["subtotal"] for item in carrinho)

    return render_template(
        "vendas/nova.html",
        produtos=produtos,
        carrinho=carrinho,
        total=total
    )


@vendas.route("/listar")
def listar_vendas():
    lista = Venda.query.order_by(Venda.id.desc()).all()
    return render_template("vendas/listar.html", vendas=lista)


@vendas.route("/<int:venda_id>")
def detalhe_venda(venda_id):
    venda = Venda.query.get_or_404(venda_id)
    return render_template("vendas/detalhe.html", venda=venda)


@vendas.route("/<int:venda_id>/cupom")
def cupom_venda(venda_id):
    venda = Venda.query.get_or_404(venda_id)
    return render_template("vendas/cupom.html", venda=venda)