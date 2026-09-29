import psycopg2
DSN = open("dsn.txt", encoding="utf-8-sig").read().strip()
conn = psycopg2.connect(DSN)
cur = conn.cursor()
cur.execute("SELECT pg_size_pretty(pg_database_size(current_database())), pg_database_size(current_database());")
print("Tamanho atual do banco:", cur.fetchone())
cur.execute("DROP TABLE IF EXISTS pedido_amostra;")
conn.commit()
print("Limpeza de qualquer tabela de teste que tenha sobrado: ok")
