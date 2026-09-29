import psycopg2
DSN = open("dsn.txt", encoding="utf-8-sig").read().strip()
conn = psycopg2.connect(DSN)
cur = conn.cursor()

with open("evidencias/a4_contraprova_seletividade.txt", "w", encoding="utf-8") as f:
    cur.execute("SELECT status, count(*), round(100.0*count(*)/sum(count(*)) over(),1) FROM pedido GROUP BY status;")
    f.write("Distribuição de status:\n")
    for r in cur.fetchall():
        f.write(f"{r}\n")

    cur.execute("""
        EXPLAIN (ANALYZE, BUFFERS)
        SELECT pedido_id, valor_produtos FROM pedido
        WHERE status IN ('pago','enviado','entregue');
    """)
    f.write("\nEXPLAIN do filtro de baixa seletividade (~82% da tabela):\n")
    for r in cur.fetchall():
        f.write(f"{r[0]}\n")

print("A4 salvo em evidencias/a4_contraprova_seletividade.txt")
print(open("evidencias/a4_contraprova_seletividade.txt", encoding="utf-8").read())
