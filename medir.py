import sys, re, os, psycopg2

DSN = open("dsn.txt", encoding="utf-8-sig").read().strip()

def tempo_e_blocos(explain_texto):
    m_tempo = re.search(r"Execution Time: ([\d.]+)", explain_texto)
    tempo = float(m_tempo.group(1)) if m_tempo else None
    m_buf = re.search(r"Buffers: (.+)", explain_texto)
    blocos = 0
    if m_buf:
        linha = m_buf.group(1)
        blocos = sum(int(x) for x in re.findall(r"shared hit=(\d+)", linha))
        blocos += sum(int(x) for x in re.findall(r"shared read=(\d+)", linha))
    return tempo, blocos

pasta = sys.argv[1]  # "antes" ou "depois"
nomes = sys.argv[2:]

os.makedirs(f"evidencias\\{pasta}", exist_ok=True)
resumo = []

for nome in nomes:
    arquivo_sql = f"sql\\{nome}.sql"
    sql = open(arquivo_sql, encoding="utf-8").read()
    sql_limpo = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))
    explain_sql = f"EXPLAIN (ANALYZE, BUFFERS) {sql_limpo}"

    tempos, blocos_lista, ultimo_texto = [], [], ""
    for execucao in range(3):
        conn = psycopg2.connect(DSN)
        cur = conn.cursor()
        cur.execute(explain_sql)
        linhas = [r[0] for r in cur.fetchall()]
        texto = "\n".join(linhas)
        conn.close()
        t, b = tempo_e_blocos(texto)
        tempos.append(t)
        blocos_lista.append(b)
        ultimo_texto = texto
        print(f"{nome} run{execucao+1}: {t} ms, {b} blocos")

    with open(f"evidencias\\{pasta}\\{nome}.txt", "w", encoding="utf-8") as f:
        f.write(ultimo_texto)

    tempos_ordenados = sorted(tempos)
    mediana = tempos_ordenados[1]
    resumo.append((nome, tempos, mediana, blocos_lista[0]))

print("\n=== RESUMO ===")
for nome, tempos, mediana, blocos in resumo:
    print(f"{nome:16s} execucoes={tempos}  mediana={mediana:.1f} ms  blocos={blocos}")

with open(f"evidencias\\resumo_{pasta}.txt", "w", encoding="utf-8") as f:
    for nome, tempos, mediana, blocos in resumo:
        f.write(f"{nome:16s} execucoes={tempos}  mediana={mediana:.1f} ms  blocos={blocos}\n")
