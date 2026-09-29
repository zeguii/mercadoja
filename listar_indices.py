import psycopg2
DSN = open("dsn.txt", encoding="utf-8-sig").read().strip()
conn = psycopg2.connect(DSN)
cur = conn.cursor()
cur.execute("SELECT indexname FROM pg_indexes WHERE tablename='pedido' ORDER BY indexname;")
for r in cur.fetchall():
    print(r[0])
