import psycopg2
DSN = open("dsn.txt", encoding="utf-8-sig").read().strip()
conn = psycopg2.connect(DSN)
cur = conn.cursor()

cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
print("Tamanho total do banco:", cur.fetchone()[0])

cur.execute("""
    SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
    FROM pg_catalog.pg_statio_user_tables
    ORDER BY pg_total_relation_size(relid) DESC
    LIMIT 10;
""")
print("\nMaiores tabelas (dados + índices):")
for r in cur.fetchall():
    print(r)
