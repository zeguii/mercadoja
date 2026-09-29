-- Q5. Produtos ativos com "fone bluetooth" no nome (case-insensitive),
-- preço entre 50 e 600, top 50 por preço crescente.
-- ILIKE com padrão '%...%' não usa B-tree; ver sql/indices.sql (pg_trgm + GIN)
-- para o índice que acelera esta consulta.
SELECT nome, preco
FROM produto
WHERE ativo = TRUE
  AND nome ILIKE '%fone bluetooth%'
  AND preco BETWEEN 50.00 AND 600.00
ORDER BY preco ASC, produto_id
LIMIT 50;
