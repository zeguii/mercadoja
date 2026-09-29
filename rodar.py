import sys, psycopg2

DSN = open("dsn.txt", encoding="utf-8-sig").read().strip()

arquivo = sys.argv[1]
sql = open(arquivo, encoding="utf-8").read()

conn = psycopg2.connect(DSN)
cur = conn.cursor()
cur.execute(sql)
colunas = [d[0] for d in cur.description]
print(" | ".join(colunas))
linhas = cur.fetchall()
for linha in linhas[:15]:
    print(linha)
print(f"\n({len(linhas)} linha(s) no total)")
