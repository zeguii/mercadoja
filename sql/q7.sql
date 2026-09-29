-- Q7. Clientes com 2+ pedidos no mesmo dia (cancelados não contam). Top 100.
-- ORDER BY com desempate explícito (cliente, dia): sem isso, o LIMIT 100
-- corta de forma não determinística entre os muitos empates de qtd_pedidos=2.
SELECT
    c.nome                    AS cliente,
    p.data_pedido::date       AS dia,
    count(*)                  AS qtd_pedidos
FROM pedido p
JOIN cliente c ON c.cliente_id = p.cliente_id
WHERE p.status <> 'cancelado'
GROUP BY c.cliente_id, c.nome, p.data_pedido::date
HAVING count(*) >= 2
ORDER BY qtd_pedidos DESC, c.cliente_id, dia
LIMIT 100;
