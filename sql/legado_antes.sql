-- Consulta legada da controladoria (ORIGINAL, sem otimização).
-- Problema: to_char(p.data_pedido, 'YYYY-MM') aplica uma função sobre a
-- coluna filtrada em TODA linha da tabela antes de comparar — o otimizador
-- não consegue usar nenhum índice de b-tree sobre data_pedido, porque o
-- valor indexado é a data crua, não o texto 'YYYY-MM' resultante da função.
-- Isso força um Seq Scan completo mesmo que o filtro (4 meses de ~30) seja
-- bastante seletivo.
SELECT
    extract(year  FROM p.data_pedido) AS ano,
    extract(month FROM p.data_pedido) AS mes,
    to_char(p.data_pedido, 'TMDay')   AS dia_semana,
    count(*)                          AS pedidos
FROM pedido p
WHERE to_char(p.data_pedido, 'YYYY-MM') IN ('2026-03','2026-04','2026-05','2026-06')
  AND p.status IN ('pago','enviado','entregue')
  AND (p.uf_entrega = 'CE' OR p.uf_entrega = 'PI' OR p.uf_entrega = 'RN' OR p.uf_entrega = 'PE')
GROUP BY 1, 2, 3
ORDER BY ano, mes, dia_semana;
