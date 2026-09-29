import psycopg2, time
DSN = open("dsn.txt", encoding="utf-8-sig").read().strip()
conn = psycopg2.connect(DSN)
cur = conn.cursor()

def medir(arquivo):
    sql_limpo = "\n".join(l for l in open(arquivo, encoding="utf-8") if not l.strip().startswith("--"))
    tempos = []
    for _ in range(3):
        cur.execute(f"EXPLAIN (ANALYZE, BUFFERS) {sql_limpo}")
        texto = "\n".join(r[0] for r in cur.fetchall())
        import re
        m = re.search(r"Execution Time: ([\d.]+)", texto)
        tempos.append(float(m.group(1)))
    return sorted(tempos)[1], texto  # mediana, último plano

med_v1, plano_v1 = medir("sql/q7.sql")
med_v2, plano_v2 = medir("sql/a3_q7_agregar_antes.sql")

resultado = f"""A3 — Q7 original (v1) vs reescrita agregando antes de juntar (v2)

Mediana v1 (original): {med_v1:.1f} ms
Mediana v2 (agregar antes): {med_v2:.1f} ms
Ganho: {(med_v1-med_v2)/med_v1*100:.1f}%

--- Plano v1 ---
{plano_v1}

--- Plano v2 ---
{plano_v2}
"""
open("evidencias/a3_reescrita_sem_indice.txt", "w", encoding="utf-8").write(resultado)
print(f"v1: {med_v1:.1f} ms | v2: {med_v2:.1f} ms | ganho: {(med_v1-med_v2)/med_v1*100:.1f}%")
