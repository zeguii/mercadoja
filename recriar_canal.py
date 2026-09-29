import psycopg2
DSN = open("dsn.txt", encoding="utf-8-sig").read().strip()
conn = psycopg2.connect(DSN)
cur = conn.cursor()
try:
    cur.execute("CREATE INDEX idx_pedido_canal_ignorado ON pedido (canal_venda);")
    conn.commit()
    print("Recriado com sucesso.")
except Exception as e:
    print("Ainda falhou:", e)
