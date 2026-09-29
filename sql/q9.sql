-- Q9 (bônus). Coorte de retenção: por mês de aquisição, quantos clientes
-- também compraram em M+1, M+2 e M+3 (só pedidos não cancelados).
WITH primeiro_pedido AS (
    SELECT cliente_id, min(date_trunc('month', data_pedido)) AS mes_aquisicao
    FROM pedido
    WHERE status <> 'cancelado'
    GROUP BY cliente_id
),
pedidos_mes AS (
    SELECT DISTINCT cliente_id, date_trunc('month', data_pedido) AS mes_pedido
    FROM pedido
    WHERE status <> 'cancelado'
)
SELECT
    pp.mes_aquisicao::date AS mes_aquisicao,
    count(DISTINCT pp.cliente_id) AS clientes_adquiridos,
    count(DISTINCT CASE WHEN pm.mes_pedido = pp.mes_aquisicao + INTERVAL '1 month' THEN pp.cliente_id END) AS retidos_m1,
    count(DISTINCT CASE WHEN pm.mes_pedido = pp.mes_aquisicao + INTERVAL '2 month' THEN pp.cliente_id END) AS retidos_m2,
    count(DISTINCT CASE WHEN pm.mes_pedido = pp.mes_aquisicao + INTERVAL '3 month' THEN pp.cliente_id END) AS retidos_m3
FROM primeiro_pedido pp
LEFT JOIN pedidos_mes pm ON pm.cliente_id = pp.cliente_id
GROUP BY pp.mes_aquisicao
ORDER BY pp.mes_aquisicao;
