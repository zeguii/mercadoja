-- Q4. Ticket médio e quantidade de pedidos por UF de entrega e canal,
-- últimos 12 meses, apenas pedidos faturados.
SELECT
    uf_entrega,
    canal_venda,
    count(*)                                                              AS qtd_pedidos,
    round(avg(valor_produtos - valor_desconto + valor_frete)::numeric, 2) AS ticket_medio
FROM pedido
WHERE data_pedido >= '2025-09-16' AND data_pedido < '2026-09-16'
  AND status IN ('pago','enviado','entregue')
GROUP BY uf_entrega, canal_venda
ORDER BY uf_entrega, canal_venda;
