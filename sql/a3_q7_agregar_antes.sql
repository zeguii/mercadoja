-- A3 — segunda versão de Q7 (a v1/original é sql/q7.sql).
-- Técnica: "agregar antes de juntar". A v1 junta pedido↔cliente para as
-- 600.000 linhas de pedido e só agrupa depois. Aqui agrupamos pedido
-- sozinho primeiro (reduzindo a, no máximo, algumas centenas de linhas —
-- só clientes com 2+ pedidos no mesmo dia) e só então juntamos com
-- cliente, que agora processa um punhado de linhas em vez de 600 mil.
-- Mesmo resultado (mesmas linhas, mesmos valores) — conferido com diff.
WITH contagem AS (
    SELECT
        cliente_id,
        data_pedido::date AS dia,
        count(*) AS qtd_pedidos
    FROM pedido
    WHERE status <> 'cancelado'
    GROUP BY cliente_id, data_pedido::date
    HAVING count(*) >= 2
)
SELECT
    c.nome AS cliente,
    ct.dia,
    ct.qtd_pedidos
FROM contagem ct
JOIN cliente c ON c.cliente_id = ct.cliente_id
ORDER BY ct.qtd_pedidos DESC, ct.cliente_id, ct.dia
LIMIT 100;
