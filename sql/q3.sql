-- Q3. Clientes com último pedido (ignorando cancelados) há mais de 90 dias
-- da data de referência (15/09/2026) e gasto total >= R$ 2000,00.
-- gasto = valor_produtos (já líquido de desconto por item) - valor_desconto (cupom) + valor_frete
WITH pedidos_validos AS (
    SELECT cliente_id, data_pedido,
           (valor_produtos - valor_desconto + valor_frete) AS valor_pedido
    FROM pedido
    WHERE status <> 'cancelado'
),
agregado AS (
    SELECT cliente_id,
           max(data_pedido)   AS ultimo_pedido,
           sum(valor_pedido)  AS total_gasto
    FROM pedidos_validos
    GROUP BY cliente_id
)
SELECT
    c.nome,
    c.cidade,
    a.ultimo_pedido::date AS data_ultimo_pedido,
    a.total_gasto
FROM agregado a
JOIN cliente c ON c.cliente_id = a.cliente_id
WHERE a.ultimo_pedido < TIMESTAMP '2026-09-15' - INTERVAL '90 days'
  AND a.total_gasto >= 2000.00
ORDER BY a.total_gasto DESC, a.cliente_id
LIMIT 500;
