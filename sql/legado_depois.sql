-- Consulta legada REESCRITA — mesmo resultado (mesmas linhas, mesmos valores).
-- Mudanças:
--   1) to_char(data_pedido,'YYYY-MM') IN (...)  -->  intervalo direto
--      [2026-03-01, 2026-07-01). Sargável: permite Index Scan / Bitmap
--      Index Scan em um índice sobre data_pedido.
--   2) (uf = 'CE' OR uf = 'PI' OR uf = 'RN' OR uf = 'PE')  -->  uf IN (...)
--      Semanticamente idêntico; deixa explícito para o planejador que é
--      uma lista de igualdade sobre a MESMA coluna (facilita Bitmap Or /
--      uso de índice composto, em vez de uma cadeia de OR).
--   3) extract(year/month) e to_char('TMDay') continuam no SELECT/GROUP BY
--      de saída — aplicar função sobre o valor JÁ FILTRADO não tem custo
--      relevante; o que precisa ser sargável é o filtro do WHERE, não a
--      projeção.
SELECT
    extract(year  FROM p.data_pedido) AS ano,
    extract(month FROM p.data_pedido) AS mes,
    to_char(p.data_pedido, 'TMDay')   AS dia_semana,
    count(*)                          AS pedidos
FROM pedido p
WHERE p.data_pedido >= TIMESTAMP '2026-03-01'
  AND p.data_pedido <  TIMESTAMP '2026-07-01'
  AND p.status IN ('pago','enviado','entregue')
  AND p.uf_entrega IN ('CE','PI','RN','PE')
GROUP BY 1, 2, 3
ORDER BY ano, mes, dia_semana;
