-- Q6. Lojas com >=5 pedidos entregues no último trimestre (16/06/2026-15/09/2026)
-- e nota média >= 4.5 nas avaliações desses pedidos.
WITH pedidos_entregues_tri AS (
    SELECT e.pedido_id
    FROM entrega e
    WHERE e.status = 'entregue'
      AND e.data_entrega >= '2026-06-16' AND e.data_entrega < '2026-09-16'
),
itens_por_loja AS (
    SELECT DISTINCT ip.pedido_id, pr.loja_id
    FROM item_pedido ip
    JOIN produto pr ON pr.produto_id = ip.produto_id
    WHERE ip.pedido_id IN (SELECT pedido_id FROM pedidos_entregues_tri)
),
contagem AS (
    SELECT loja_id, count(DISTINCT pedido_id) AS pedidos_entregues
    FROM itens_por_loja
    GROUP BY loja_id
),
notas AS (
    SELECT pr.loja_id, avg(av.nota) AS nota_media
    FROM avaliacao av
    JOIN produto pr ON pr.produto_id = av.produto_id
    WHERE av.pedido_id IN (SELECT pedido_id FROM pedidos_entregues_tri)
    GROUP BY pr.loja_id
)
SELECT
    l.nome_fantasia          AS loja,
    l.plano_assinatura       AS plano,
    c.pedidos_entregues,
    round(n.nota_media::numeric, 2) AS nota_media
FROM contagem c
JOIN notas n ON n.loja_id = c.loja_id
JOIN loja l  ON l.loja_id = c.loja_id
WHERE c.pedidos_entregues >= 5 AND n.nota_media >= 4.5
ORDER BY nota_media DESC, pedidos_entregues DESC, c.loja_id
LIMIT 100;
