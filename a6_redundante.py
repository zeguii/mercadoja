import psycopg2
DSN = open("dsn.txt", encoding="utf-8-sig").read().strip()
conn = psycopg2.connect(DSN)
cur = conn.cursor()

log = []

cur.execute("DROP TABLE IF EXISTS pedido_amostra;")
cur.execute("CREATE TABLE pedido_amostra AS SELECT * FROM pedido LIMIT 5000;")
conn.commit()
log.append("Tabela de amostra criada com 5.000 linhas (só para o experimento da A6).")

cur.execute("CREATE INDEX ix_amostra_2col ON pedido_amostra (status, data_pedido);")
conn.commit()
cur.execute("CREATE INDEX ix_amostra_3col ON pedido_amostra (status, data_pedido, uf_entrega);")
conn.commit()
log.append("Criados: ix_amostra_2col (status, data_pedido) e ix_amostra_3col (status, data_pedido, uf_entrega).")
log.append("ix_amostra_2col é PREFIXO de ix_amostra_3col.")

cur.execute("""
    SELECT indexname, pg_size_pretty(pg_relation_size(indexname::regclass))
    FROM pg_indexes WHERE tablename='pedido_amostra';
""")
log.append("\nTamanho de cada índice:")
for r in cur.fetchall():
    log.append(str(r))

cur.execute("ANALYZE pedido_amostra;")
cur.execute("DROP INDEX ix_amostra_2col;")
conn.commit()
log.append("\nix_amostra_2col REMOVIDO. Testando se consulta por status+data ainda usa o índice de 3 colunas:")

cur.execute("""
    EXPLAIN SELECT count(*) FROM pedido_amostra
    WHERE status IN ('pago','enviado','entregue')
      AND data_pedido >= '2026-06-01' AND data_pedido < '2026-07-01';
""")
for r in cur.fetchall():
    log.append(r[0])

cur.execute("DROP TABLE pedido_amostra;")
conn.commit()
log.append("\nTabela de amostra removida — espaço liberado de volta.")

texto = "\n".join(log)
open("evidencias/a6_indice_redundante.txt", "w", encoding="utf-8").write(texto)
print(texto)
