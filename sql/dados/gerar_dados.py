#!/usr/bin/env python3
"""
Gerador de dados sintéticos para o MercadoJá.

Reprodutibilidade: toda a aleatoriedade usa random.Random(SEED) — a mesma
SEED sempre produz o mesmo banco (linha por linha), independente da máquina.

Estratégia de carga: gera CSVs em memória/disco e usa COPY (via psycopg2
copy_expert), que é ordens de grandeza mais rápido que INSERT linha a linha
para os volumes exigidos (até 1,5M+ linhas em item_pedido).

Uso:
    python3 gerar_dados.py --scale 1.0 --dsn "dbname=mercadoja user=postgres password=postgres host=localhost"

--scale 1.0  -> volume cheio do contrato (100k clientes, 600k pedidos, ...)
--scale 0.1  -> 10% do volume, útil para testar o pipeline rapidamente
                (a redução de até 50% é aceita pelo enunciado, com justificativa
                 de limitação de hardware, mantendo as proporções)
"""
import argparse
import csv
import io
import random
import sys
from datetime import date, datetime, timedelta

import psycopg2

SEED = 20260915  # data de referência do trabalho, usada como semente fixa

CIDADES = [
    # (cidade, uf, peso)
    ("Fortaleza", "CE", 45.0),
    ("Caucaia", "CE", 8.0),
    ("Maracanaú", "CE", 6.0),
    ("Sobral", "CE", 5.0),
    ("Juazeiro do Norte", "CE", 6.0),
    ("Crato", "CE", 4.0),
    ("Iguatu", "CE", 3.0),
    ("Quixadá", "CE", 3.0),
    ("Canindé", "CE", 2.5),
    ("Aracati", "CE", 2.5),
    ("Teresina", "PI", 6.0),
    ("Natal", "RN", 5.0),
    ("Recife", "PE", 4.0),
]

CATEGORIAS_RAIZ = [
    "Eletrônicos", "Casa e Cozinha", "Moda", "Beleza e Cuidado Pessoal",
    "Alimentos e Bebidas", "Esporte e Lazer", "Bebês e Crianças",
    "Pet Shop", "Papelaria e Escritório", "Automotivo",
    "Ferramentas e Construção", "Livros e Papelaria Criativa",
]
# distribui 39 categorias-filha entre as 12 raízes (mín. 2, o resto proporcional)
LEAVES_PER_ROOT = [4, 3, 5, 3, 4, 3, 3, 2, 3, 3, 3, 3]  # soma = 39

PLANOS = ["gratis", "basico", "pro", "enterprise"]
PLANOS_PESOS = [35, 35, 22, 8]

SEGMENTOS = ["novo", "regular", "vip", "inativo"]
SEGMENTOS_PESOS = [25, 45, 15, 15]

METODOS_PAGAMENTO = ["pix", "cartao_credito", "cartao_debito", "boleto", "dinheiro"]
METODOS_PESOS = [40, 35, 15, 8, 2]

TRANSPORTADORAS = ["Correios", "Loggi", "JadLog", "TransCE Express", "Rota Nordeste"]

DATA_INICIO_PEDIDOS = date(2024, 3, 1)
DATA_REFERENCIA = date(2026, 9, 15)

PRODUTO_ADJETIVOS = ["Pro", "Plus", "Max", "Lite", "X", "2.0", "Premium", "Compacto"]
PRODUTO_NOMES_BASE = [
    "Fone Bluetooth", "Fone de Ouvido com Fio", "Caixa de Som Bluetooth",
    "Smartwatch", "Carregador Portátil", "Cabo USB-C", "Mouse sem Fio",
    "Teclado Mecânico", "Panela de Pressão", "Air Fryer", "Jogo de Facas",
    "Camiseta Básica", "Tênis Esportivo", "Mochila", "Shampoo", "Perfume",
    "Ração para Cães", "Cadeira de Escritório", "Furadeira", "Livro de Receitas",
]


def rng():
    return random.Random(SEED)


def escolha_ponderada(r, opcoes, pesos):
    return r.choices(opcoes, weights=pesos, k=1)[0]


def gerar_categorias(r):
    linhas = []  # (id, nome, pai_id)
    cat_id = 1
    raiz_ids = []
    for nome in CATEGORIAS_RAIZ:
        linhas.append((cat_id, nome, None))
        raiz_ids.append(cat_id)
        cat_id += 1
    for raiz_idx, n_filhas in enumerate(LEAVES_PER_ROOT):
        pai_id = raiz_ids[raiz_idx]
        raiz_nome = CATEGORIAS_RAIZ[raiz_idx]
        for i in range(n_filhas):
            linhas.append((cat_id, f"{raiz_nome} - Sub {i+1}", pai_id))
            cat_id += 1
    return linhas, raiz_ids


def cidade_uf_aleatoria(r):
    nomes = [c[0] for c in CIDADES]
    pesos = [c[2] for c in CIDADES]
    escolhida = escolha_ponderada(r, nomes, pesos)
    uf = next(c[1] for c in CIDADES if c[0] == escolhida)
    return escolhida, uf


def gerar_clientes(r, n):
    linhas = []
    for i in range(1, n + 1):
        cidade, uf = cidade_uf_aleatoria(r)
        dias_atras = r.randint(0, (DATA_REFERENCIA - DATA_INICIO_PEDIDOS).days + 200)
        data_cad = DATA_REFERENCIA - timedelta(days=dias_atras)
        linhas.append((
            i, f"Cliente {i}", f"cliente{i}@mail.com", f"85{r.randint(900000000,999999999)}",
            cidade, uf, data_cad.isoformat(),
            escolha_ponderada(r, SEGMENTOS, SEGMENTOS_PESOS),
        ))
    return linhas


def gerar_lojas(r, n):
    linhas = []
    qualidade = {}  # loja_id -> tier de nota média ('boa','media','ruim')
    for i in range(1, n + 1):
        cidade, uf = cidade_uf_aleatoria(r)
        dias_atras = r.randint(0, 900)
        data_ades = DATA_REFERENCIA - timedelta(days=dias_atras)
        cnpj = f"{r.randint(10**13, 10**14 - 1)}"
        ativa = r.random() < 0.9
        linhas.append((
            i, f"Loja {i} Ltda", cnpj, cidade, uf,
            escolha_ponderada(r, PLANOS, PLANOS_PESOS), data_ades.isoformat(), ativa,
        ))
        tier = escolha_ponderada(r, ["boa", "media", "ruim"], [15, 75, 10])
        qualidade[i] = tier
    return linhas, qualidade


def gerar_produtos(r, n, n_lojas, categorias_folha):
    linhas = []
    # garante um lote de produtos "fone bluetooth" com nome/case variados p/ Q5
    nomes_alvo = ["Fone Bluetooth", "FONE BLUETOOTH", "fone bluetooth", "Fone bluetooth In-Ear"]
    for i in range(1, n + 1):
        loja_id = r.randint(1, n_lojas)
        categoria_id = r.choice(categorias_folha)
        if i <= 60:
            base = r.choice(nomes_alvo)
            preco = round(r.uniform(45, 650), 2)  # parte propositalmente fora do range 50-600
        else:
            base = r.choice(PRODUTO_NOMES_BASE)
            preco = round(r.uniform(15, 2500), 2)
        nome = f"{base} {r.choice(PRODUTO_ADJETIVOS)} {i}"
        estoque = r.randint(0, 500)
        ativo = r.random() < 0.92
        dias_atras = r.randint(0, 1000)
        data_criacao = datetime.combine(DATA_REFERENCIA, datetime.min.time()) - timedelta(days=dias_atras)
        linhas.append((i, loja_id, categoria_id, nome, f"Descrição do produto {i}",
                        preco, estoque, ativo, data_criacao.isoformat()))
    return linhas


def peso_mes(ano, mes):
    """Fator de sazonalidade: leve crescimento mensal + pico nov/dez."""
    meses_desde_inicio = (ano - 2024) * 12 + (mes - 3)
    crescimento = (1.02 ** max(meses_desde_inicio, 0))
    pico = 1.5 if mes in (11, 12) else 1.0
    return crescimento * pico


def gerar_calendario_pedidos(r, n_pedidos):
    """Distribui os N pedidos entre os meses do período, respeitando a sazonalidade."""
    meses = []
    y, m = 2024, 3
    while (y, m) <= (2026, 9):
        meses.append((y, m))
        m += 1
        if m == 13:
            m = 1
            y += 1
    pesos = [peso_mes(y, m) for y, m in meses]
    total_peso = sum(pesos)
    datas = []
    for (y, m), w in zip(meses, pesos):
        qtd_mes = round(n_pedidos * w / total_peso)
        if y == 2026 and m == 9:
            dia_max = 15
        else:
            dia_max = 28
        for _ in range(qtd_mes):
            dia = r.randint(1, dia_max)
            hora = r.randint(7, 23)
            minuto = r.randint(0, 59)
            datas.append(datetime(y, m, dia, hora, minuto))
    r.shuffle(datas)
    return datas[:n_pedidos]


def status_pedido(r):
    x = r.random()
    if x < 0.14:
        return "cancelado"
    elif x < 0.14 + 0.04:
        return "carrinho"  # não faturado, não cancelado (abandono)
    elif x < 0.14 + 0.04 + 0.10:
        return "pago"
    elif x < 0.14 + 0.04 + 0.10 + 0.25:
        return "enviado"
    else:
        return "entregue"


def gerar_pedidos_e_itens(r, n_pedidos, n_clientes, produtos_por_loja_cache, produtos, qualidade_loja):
    datas = gerar_calendario_pedidos(r, n_pedidos)
    pedidos = []
    itens = []
    pagamentos = []
    entregas = []
    item_id = 1
    pagamento_id = 1
    entrega_id = 1

    n_produtos = len(produtos)

    for pid in range(1, n_pedidos + 1):
        cliente_id = r.randint(1, n_clientes)
        data_pedido = datas[pid - 1]
        status = status_pedido(r)
        canal = escolha_ponderada(r, ["aplicativo", "site", "whatsapp"], [60, 25, 15])
        # entrega geralmente na mesma região do cliente (aproximação: sorteia de novo
        # com mesma distribuição, o que já reproduz a concentração em Fortaleza)
        cidade_entrega, uf_entrega = cidade_uf_aleatoria(r)
        frete_gratis = r.random() < 0.37
        valor_frete = 0.0 if frete_gratis else round(r.uniform(7.99, 22.90), 2)
        valor_desconto_pedido = 0.0 if r.random() > 0.10 else round(r.uniform(5, 50), 2)

        n_itens = r.choices([1, 2, 3, 4, 5, 6], weights=[25, 30, 20, 12, 8, 5], k=1)[0]
        valor_produtos = 0.0
        for _ in range(n_itens):
            produto_id = r.randint(1, n_produtos)
            preco_unit = produtos[produto_id - 1][5]  # coluna preco no tuple gerado
            qtd = r.choices([1, 2, 3], weights=[70, 22, 8], k=1)[0]
            desconto_item = round(preco_unit * qtd * r.uniform(0, 0.08), 2) if r.random() < 0.2 else 0.0
            itens.append((item_id, pid, produto_id, qtd, preco_unit, desconto_item))
            valor_produtos += qtd * preco_unit - desconto_item
            item_id += 1
        valor_produtos = round(valor_produtos, 2)
        # cupom de pedido nunca pode exceder o valor dos produtos (evita total negativo)
        valor_desconto_pedido = min(valor_desconto_pedido, round(valor_produtos * 0.3, 2))

        pedidos.append((pid, cliente_id, data_pedido.isoformat(), status, canal,
                         cidade_entrega, uf_entrega, valor_produtos, valor_frete, valor_desconto_pedido))

        if status in ("pago", "enviado", "entregue"):
            pagamentos.append((
                pagamento_id, pid, escolha_ponderada(r, METODOS_PAGAMENTO, METODOS_PESOS),
                "aprovado", round(valor_produtos + valor_frete - valor_desconto_pedido, 2),
                (data_pedido + timedelta(minutes=r.randint(1, 120))).isoformat(),
            ))
            pagamento_id += 1
        if status in ("enviado", "entregue"):
            data_envio = data_pedido + timedelta(days=r.randint(1, 3))
            data_entrega_dt = data_envio + timedelta(days=r.randint(1, 8)) if status == "entregue" else None
            entregas.append((
                entrega_id, pid, r.choice(TRANSPORTADORAS),
                "entregue" if status == "entregue" else "em_transito",
                data_envio.isoformat(), data_entrega_dt.isoformat() if data_entrega_dt else "",
                valor_frete,
            ))
            entrega_id += 1

    return pedidos, itens, pagamentos, entregas


def gerar_avaliacoes(r, n_alvo, pedidos, itens, qualidade_loja, produtos):
    # só pedidos entregues podem ser avaliados
    entregues = [p for p in pedidos if p[3] == "entregue"]
    itens_por_pedido = {}
    for it in itens:
        itens_por_pedido.setdefault(it[1], []).append(it)

    avaliacoes = []
    aval_id = 1
    tentativas = 0
    while len(avaliacoes) < n_alvo and tentativas < n_alvo * 3:
        tentativas += 1
        pedido = r.choice(entregues)
        pedido_id, cliente_id = pedido[0], pedido[1]
        seus_itens = itens_por_pedido.get(pedido_id, [])
        if not seus_itens:
            continue
        item = r.choice(seus_itens)
        produto_id = item[2]
        loja_id = produtos[produto_id - 1][1]
        tier = qualidade_loja.get(loja_id, "media")
        if tier == "boa":
            nota = r.choices([3, 4, 5], weights=[5, 30, 65], k=1)[0]
        elif tier == "ruim":
            nota = r.choices([1, 2, 3, 4], weights=[25, 35, 30, 10], k=1)[0]
        else:
            nota = r.choices([3, 4, 5], weights=[20, 45, 35], k=1)[0]
        data_pedido_dt = datetime.fromisoformat(pedido[2])
        data_aval = data_pedido_dt + timedelta(days=r.randint(2, 20))
        avaliacoes.append((aval_id, pedido_id, produto_id, cliente_id, nota,
                            "Bom produto." if nota >= 4 else "Poderia ser melhor.",
                            data_aval.isoformat()))
        aval_id += 1
    return avaliacoes


def copy_rows(conn, tabela, colunas, linhas):
    buf = io.StringIO()
    writer = csv.writer(buf, delimiter="\t", lineterminator="\n")
    for linha in linhas:
        writer.writerow(["" if v is None else v for v in linha])
    buf.seek(0)
    with conn.cursor() as cur:
        cur.copy_expert(
            f"COPY {tabela} ({','.join(colunas)}) FROM STDIN WITH (FORMAT csv, DELIMITER E'\\t', NULL '')",
            buf,
        )
    conn.commit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--dsn", type=str, required=True)
    args = ap.parse_args()

    r = rng()
    n_clientes = int(100_000 * args.scale)
    n_lojas = int(5_000 * args.scale)
    n_produtos = int(40_000 * args.scale)
    n_pedidos = int(600_000 * args.scale)
    n_avaliacoes = int(250_000 * args.scale)

    print(f"[scale={args.scale}] clientes={n_clientes} lojas={n_lojas} "
          f"produtos={n_produtos} pedidos={n_pedidos} avaliacoes={n_avaliacoes}", file=sys.stderr)

    conn = psycopg2.connect(args.dsn)

    print("Gerando categorias...", file=sys.stderr)
    categorias, raiz_ids = gerar_categorias(r)
    categorias_folha = [c[0] for c in categorias if c[2] is not None]
    copy_rows(conn, "categoria", ["categoria_id", "nome", "categoria_pai_id"], categorias)

    print("Gerando clientes...", file=sys.stderr)
    clientes = gerar_clientes(r, n_clientes)
    copy_rows(conn, "cliente",
              ["cliente_id", "nome", "email", "telefone", "cidade", "uf", "data_cadastro", "segmento"],
              clientes)

    print("Gerando lojas...", file=sys.stderr)
    lojas, qualidade_loja = gerar_lojas(r, n_lojas)
    copy_rows(conn, "loja",
              ["loja_id", "nome_fantasia", "cnpj", "cidade", "uf", "plano_assinatura", "data_adesao", "ativa"],
              lojas)

    print("Gerando produtos...", file=sys.stderr)
    produtos = gerar_produtos(r, n_produtos, n_lojas, categorias_folha)
    copy_rows(conn, "produto",
              ["produto_id", "loja_id", "categoria_id", "nome", "descricao", "preco", "estoque", "ativo", "data_criacao"],
              produtos)

    print("Gerando pedidos, itens, pagamentos e entregas (pode levar alguns minutos)...", file=sys.stderr)
    pedidos, itens, pagamentos, entregas = gerar_pedidos_e_itens(
        r, n_pedidos, n_clientes, None, produtos, qualidade_loja)
    copy_rows(conn, "pedido",
              ["pedido_id", "cliente_id", "data_pedido", "status", "canal_venda",
               "cidade_entrega", "uf_entrega", "valor_produtos", "valor_frete", "valor_desconto"],
              pedidos)
    copy_rows(conn, "item_pedido",
              ["item_pedido_id", "pedido_id", "produto_id", "quantidade", "preco_unitario", "desconto_item"],
              itens)
    copy_rows(conn, "pagamento",
              ["pagamento_id", "pedido_id", "metodo", "status", "valor", "data_pagamento"],
              pagamentos)
    copy_rows(conn, "entrega",
              ["entrega_id", "pedido_id", "transportadora", "status", "data_envio", "data_entrega", "custo_frete"],
              entregas)

    print("Gerando avaliações...", file=sys.stderr)
    avaliacoes = gerar_avaliacoes(r, n_avaliacoes, pedidos, itens, qualidade_loja, produtos)
    copy_rows(conn, "avaliacao",
              ["avaliacao_id", "pedido_id", "produto_id", "cliente_id", "nota", "comentario", "data_avaliacao"],
              avaliacoes)

    print("Ajustando sequences...", file=sys.stderr)
    with conn.cursor() as cur:
        for tabela, coluna in [
            ("cliente", "cliente_id"), ("loja", "loja_id"), ("categoria", "categoria_id"),
            ("produto", "produto_id"), ("pedido", "pedido_id"), ("item_pedido", "item_pedido_id"),
            ("pagamento", "pagamento_id"), ("entrega", "entrega_id"), ("avaliacao", "avaliacao_id"),
        ]:
            cur.execute(f"SELECT setval(pg_get_serial_sequence('{tabela}','{coluna}'), "
                        f"COALESCE((SELECT MAX({coluna}) FROM {tabela}), 1))")
    conn.commit()

    print("Carga concluída.", file=sys.stderr)
    conn.close()


if __name__ == "__main__":
    main()
