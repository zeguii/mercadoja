import psycopg2
DSN = "postgresql://neondb_owner:npg_FtYXVakmNc72@ep-damp-heart-b69b5ngm-pooler.c-2.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
conn = psycopg2.connect(DSN)
cur = conn.cursor()
cur.execute("""
SELECT 'cliente', count(*) FROM cliente
UNION ALL SELECT 'loja', count(*) FROM loja
UNION ALL SELECT 'produto', count(*) FROM produto
UNION ALL SELECT 'pedido', count(*) FROM pedido
UNION ALL SELECT 'item_pedido', count(*) FROM item_pedido
UNION ALL SELECT 'pagamento', count(*) FROM pagamento
UNION ALL SELECT 'entrega', count(*) FROM entrega
UNION ALL SELECT 'avaliacao', count(*) FROM avaliacao
""")
for r in cur.fetchall():
    print(r)
