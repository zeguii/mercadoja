import psycopg2
DSN = open("dsn.txt", encoding="utf-8-sig").read().strip()
conn = psycopg2.connect(DSN)
cur = conn.cursor()

log = []

cur.execute("SELECT pg_size_pretty(pg_relation_size('idx_pedido_canal_ignorado'::regclass));")
log.append(f"Tamanho de idx_pedido_canal_ignorado (antes de soltar): {cur.fetchone()[0]}")

cur.execute("DROP INDEX idx_pedido_canal_ignorado;")
conn.commit()
log.append("idx_pedido_canal_ignorado removido temporariamente (espaço liberado).")

cur.execute("CREATE INDEX idx_pedido_status_data ON pedido (status, data_pedido);")
conn.commit()
log.append("idx_pedido_status_data (status, data_pedido) criado — é PREFIXO de idx_pedido_status_data_uf.")

cur.execute("""
    SELECT indexname, pg_size_pretty(pg_relation_size(indexname::regclass))
    FROM pg_indexes WHERE tablename='pedido' AND indexname LIKE 'idx_pedido_status%';
""")
log.append("\nTamanho dos índices envolvidos:")
for r in cur.fetchall():
    log.append(str(r))

cur.execute("DROP INDEX idx_pedido_status_data;")
conn.commit()
log.append("\nidx_pedido_status_data REMOVIDO. Testando se consulta por status+data ainda usa o índice de 3 colunas:")

cur.execute("""
    EXPLAIN SELECT count(*) FROM pedido
    WHERE status IN ('pago','enviado','entregue')
      AND data_pedido >= '2026-06-01' AND data_pedido < '2026-07-01';
""")
for r in cur.fetchall():
    log.append(r[0])

cur.execute("CREATE INDEX idx_pedido_canal_ignorado ON pedido (canal_venda);")
conn.commit()
log.append("\nidx_pedido_canal_ignorado recriado (voltamos ao estado original de sql/indices.sql).")

texto = "\n".join(log)
open("evidencias/a6_indice_redundante.txt", "w", encoding="utf-8").write(texto)
print(texto)
