-- Q8. Top 3 produtos mais vendidos por categoria raiz em 2026 (pedidos faturados).
WITH vendas AS (
    SELECT
        cat_raiz.nome AS categoria_raiz,
        pr.produto_id,
        pr.nome       AS produto,
        sum(ip.quantidade) AS unidades
    FROM item_pedido ip
    JOIN pedido p          ON p.pedido_id = ip.pedido_id
    JOIN produto pr        ON pr.produto_id = ip.produto_id
    JOIN categoria cat_f   ON cat_f.categoria_id = pr.categoria_id
    JOIN categoria cat_raiz ON cat_raiz.categoria_id = COALESCE(cat_f.categoria_pai_id, cat_f.categoria_id)
    WHERE p.status IN ('pago','enviado','entregue')
      AND p.data_pedido >= '2026-01-01' AND p.data_pedido < '2027-01-01'
    GROUP BY cat_raiz.nome, pr.produto_id, pr.nome
),
ranqueado AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY categoria_raiz ORDER BY unidades DESC, produto_id) AS posicao
    FROM vendas
)
SELECT categoria_raiz, produto, unidades, posicao
FROM ranqueado
WHERE posicao <= 3
ORDER BY categoria_raiz, posicao;
