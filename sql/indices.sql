-- =====================================================================
-- MercadoJá — Índices de performance
-- Criados SOMENTE após medir a linha de base (evidencias/antes/).
-- Cada índice traz: coluna(s), tipo, consulta(s) que atende e por quê.
-- =====================================================================

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ---------------------------------------------------------------------
-- 1) idx_pedido_status_data_uf  (B-tree composto)
--    Atende: Q1, Q2, Q4, Q8, legado_depois — todas filtram
--    status IN (...) + intervalo de data_pedido; a legada também filtra
--    uf_entrega IN (...).
--    Ordem das colunas: status primeiro (poucas listas de igualdade),
--    depois data_pedido (o intervalo, mais seletivo: 4 de ~30 meses),
--    depois uf_entrega (igualdade extra usada só pela legada).
--    Uma consulta que filtra só por (status, data_pedido) já usa este
--    índice pelo prefixo — por isso ele TAMBÉM cobre Q1/Q2/Q4/Q8, que
--    não filtram uf_entrega.
CREATE INDEX idx_pedido_status_data_uf
    ON pedido (status, data_pedido, uf_entrega);

-- ---------------------------------------------------------------------
-- 1b) idx_pedido_status_data — NÃO criado na versão final.
--    Testado na Análise A6 (evidencias/a6_indice_redundante.txt): tem o
--    MESMO PREFIXO do índice acima (status, data_pedido) e ocupava 22 MB.
--    Depois de DROPADO, o EXPLAIN de uma consulta que filtra só por
--    status+data (ex.: Q1) continuou usando idx_pedido_status_data_uf via
--    Index Only Scan, sem nenhuma mudança de custo. Conclusão: era
--    redundante e foi removido — por isso NÃO aparece como CREATE INDEX
--    aqui na versão final do script.

-- ---------------------------------------------------------------------
-- 2) idx_pedido_cliente_data (B-tree composto)
--    Atende: Q3 (último pedido e total gasto por cliente),
--    Q7 (pedidos por cliente e dia), Q9 (primeiro pedido por cliente).
--    cliente_id é FK e o Postgres NÃO cria índice automático para FKs;
--    sem isso, agregações "por cliente" exigem Seq Scan + hash aggregate
--    na tabela inteira de pedidos.
CREATE INDEX idx_pedido_cliente_data
    ON pedido (cliente_id, data_pedido);

-- ---------------------------------------------------------------------
-- 3) idx_item_pedido_produto (B-tree)
--    Atende: Q1, Q2, Q8 — todas agregam item_pedido agrupando por
--    produto_id. item_pedido é a maior tabela (1,58M linhas); sem este
--    índice, o hash join com produto força Seq Scan na tabela inteira.
CREATE INDEX idx_item_pedido_produto
    ON item_pedido (produto_id);

-- ---------------------------------------------------------------------
-- 4) idx_item_pedido_pedido (B-tree)
--    Atende: junções item_pedido -> pedido (Q1, Q2, Q3, Q6, Q8) e o
--    filtro "pedido_id IN (subconsulta)" de Q6.
CREATE INDEX idx_item_pedido_pedido
    ON item_pedido (pedido_id);

-- ---------------------------------------------------------------------
-- 5) idx_produto_categoria (B-tree)
--    Atende: Q1, Q2, Q8 — junção produto -> categoria para achar a
--    categoria raiz de cada produto vendido.
CREATE INDEX idx_produto_categoria
    ON produto (categoria_id);

-- ---------------------------------------------------------------------
-- 6) idx_produto_loja (B-tree)
--    Atende: Q2 (nome da loja do produto), Q6 (produto -> loja).
CREATE INDEX idx_produto_loja
    ON produto (loja_id);

-- ---------------------------------------------------------------------
-- 7) idx_produto_nome_trgm (GIN de trigramas — pg_trgm)
--    Atende: Q5 — WHERE nome ILIKE '%fone bluetooth%'.
--    B-tree não serve para '%texto%' (não há prefixo fixo para descer a
--    árvore). GIN de trigramas indexa pedaços de 3 caracteres do nome e
--    permite o Postgres localizar candidatos sem varrer a tabela inteira,
--    via Bitmap Index Scan + Recheck.
CREATE INDEX idx_produto_nome_trgm
    ON produto USING gin (nome gin_trgm_ops);

-- ---------------------------------------------------------------------
-- 8) idx_produto_ativo_preco (B-tree PARCIAL)
--    Atende: Q5 também filtra ativo = TRUE e preco BETWEEN 50 E 600.
--    Parcial porque a maioria das consultas de catálogo do site só olha
--    produtos ativos (~92% da tabela) — ainda assim vale a pena porque
--    combinado ao filtro de preço reduz bastante o conjunto candidato
--    antes do Recheck do índice de trigrama.
CREATE INDEX idx_produto_ativo_preco
    ON produto (preco)
    WHERE ativo = TRUE;

-- ---------------------------------------------------------------------
-- 9) idx_entrega_status_data (B-tree composto)
--    Atende: Q6 — entregas com status = 'entregue' e data_entrega no
--    último trimestre.
CREATE INDEX idx_entrega_status_data
    ON entrega (status, data_entrega);

-- ---------------------------------------------------------------------
-- 10) idx_entrega_pedido (B-tree)
--    Atende: junção entrega -> pedido usada indiretamente em Q6.
CREATE INDEX idx_entrega_pedido
    ON entrega (pedido_id);

-- ---------------------------------------------------------------------
-- 11) idx_avaliacao_produto e idx_avaliacao_pedido (B-tree)
--    Atende: Q6 — nota média por loja (via produto) das avaliações dos
--    pedidos entregues no trimestre.
CREATE INDEX idx_avaliacao_produto
    ON avaliacao (produto_id);
CREATE INDEX idx_avaliacao_pedido
    ON avaliacao (pedido_id);

-- ---------------------------------------------------------------------
-- 12) idx_pagamento_pedido (B-tree)
--    Sem consulta obrigatória exige isso diretamente, mas é FK e, na
--    prática, a falta desse índice foi flagrante durante o desenvolvimento:
--    um DELETE de 50 mil pedidos travou minutos fazendo Seq Scan em
--    pagamento (492 mil linhas) a cada linha apagada, para checar a
--    integridade referencial. Documentado aqui como lição do próprio
--    trabalho: FK sem índice on the "lado N" pode inviabilizar
--    manutenção (DELETE/UPDATE em cascata), não só leitura.
CREATE INDEX idx_pagamento_pedido
    ON pagamento (pedido_id);

-- =====================================================================
-- A4 — Contraprova de seletividade (índice que o planejador ignora)
-- =====================================================================
-- pedido.canal_venda tem só 3 valores (aplicativo ~60%, site ~25%,
-- whatsapp ~15%) — nenhum filtro por um único canal é seletivo o
-- suficiente (a MELHOR seletividade, whatsapp, ainda devolve ~15% da
-- tabela). Criado de propósito para provar, com EXPLAIN, que o Postgres
-- prefere Seq Scan mesmo com o índice disponível (ver RELATORIO.pdf,
-- Análise A4, e evidencias/a4_contraprova_seletividade.txt).
CREATE INDEX idx_pedido_canal_ignorado
    ON pedido (canal_venda);

ANALYZE;
