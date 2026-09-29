-- Q1. Relatório da diretoria: receita líquida, pedidos e itens vendidos
-- por categoria raiz, últimos 12 meses (16/09/2025 a 15/09/2026), só faturados.
SELECT
    cat_raiz.nome                              AS categoria_raiz,
    count(DISTINCT p.pedido_id)                AS numero_pedidos,
    sum(ip.quantidade)                         AS itens_vendidos,
    sum(ip.quantidade * ip.preco_unitario - ip.desconto_item) AS receita_liquida
FROM item_pedido ip
JOIN pedido p        ON p.pedido_id = ip.pedido_id
JOIN produto pr       ON pr.produto_id = ip.produto_id
JOIN categoria cat_f  ON cat_f.categoria_id = pr.categoria_id
JOIN categoria cat_raiz ON cat_raiz.categoria_id = COALESCE(cat_f.categoria_pai_id, cat_f.categoria_id)
WHERE p.data_pedido >= '2025-09-16' AND p.data_pedido < '2026-09-16'
  AND p.status IN ('pago','enviado','entregue')
GROUP BY cat_raiz.nome
ORDER BY receita_liquida DESC;
