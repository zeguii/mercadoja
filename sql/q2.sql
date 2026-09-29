-- Q2. Top 20 produtos mais vendidos em unidades, últimos 12 meses (mesmos filtros de Q1)
SELECT
    pr.nome                                                    AS produto,
    l.nome_fantasia                                            AS loja,
    sum(ip.quantidade)                                         AS unidades,
    sum(ip.quantidade * ip.preco_unitario - ip.desconto_item)  AS receita
FROM item_pedido ip
JOIN pedido p   ON p.pedido_id = ip.pedido_id
JOIN produto pr ON pr.produto_id = ip.produto_id
JOIN loja l     ON l.loja_id = pr.loja_id
WHERE p.data_pedido >= '2025-09-16' AND p.data_pedido < '2026-09-16'
  AND p.status IN ('pago','enviado','entregue')
GROUP BY pr.produto_id, pr.nome, l.nome_fantasia
ORDER BY unidades DESC, pr.produto_id
LIMIT 20;
