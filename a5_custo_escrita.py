import psycopg2, time
DSN = open("dsn.txt", encoding="utf-8-sig").read().strip()
conn = psycopg2.connect(DSN)
conn.autocommit = True
cur = conn.cursor()

log = []

cur.execute("DROP TABLE IF EXISTS pedido_teste_sem_idx, pedido_teste_com_idx;")
cur.execute("CREATE TABLE pedido_teste_sem_idx (LIKE pedido INCLUDING DEFAULTS);")
cur.execute("CREATE TABLE pedido_teste_com_idx (LIKE pedido INCLUDING DEFAULTS);")
cur.execute("CREATE INDEX ix1 ON pedido_teste_com_idx (status, data_pedido);")
cur.execute("CREATE INDEX ix2 ON pedido_teste_com_idx (cliente_id, data_pedido);")
cur.execute("CREATE INDEX ix3 ON pedido_teste_com_idx (uf_entrega);")
log.append("Duas tabelas de teste criadas (mesma estrutura de pedido, vazias): pedido_teste_sem_idx (0 índices extras) e pedido_teste_com_idx (3 índices).")

def inserir(tabela, n):
    sql = f"""
        INSERT INTO {tabela} (cliente_id, data_pedido, status, canal_venda, cidade_entrega, uf_entrega, valor_produtos, valor_frete, valor_desconto)
        SELECT (random()*99999+1)::bigint, '2026-09-16'::timestamp + (n || ' seconds')::interval,
               'pago', 'aplicativo', 'Fortaleza', 'CE', 100.00, 10.00, 0
        FROM generate_series(1,{n}) n;
    """
    inicio = time.perf_counter()
    cur.execute(sql)
    fim = time.perf_counter()
    return (fim - inicio) * 1000

t_sem = inserir("pedido_teste_sem_idx", 10000)
log.append(f"(i) SEM índices — inserir 10.000 linhas: {t_sem:.1f} ms")

t_com = inserir("pedido_teste_com_idx", 10000)
log.append(f"(ii) COM 3 índices — inserir 10.000 linhas: {t_com:.1f} ms")

razao = t_com / t_sem
log.append(f"\nCom índices foi {razao:.2f}x mais lento.")

cur.execute("DROP TABLE pedido_teste_sem_idx, pedido_teste_com_idx;")
log.append("Tabelas de teste removidas — espaço liberado.")

texto = "\n".join(log)
open("evidencias/a5_custo_escrita.txt", "w", encoding="utf-8").write(texto)
print(texto)
