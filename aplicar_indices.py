import psycopg2
DSN = open("dsn.txt", encoding="utf-8-sig").read().strip()
sql = open("sql/indices.sql", encoding="utf-8").read()
conn = psycopg2.connect(DSN)
cur = conn.cursor()
cur.execute(sql)
conn.commit()
print("Índices aplicados com sucesso")
