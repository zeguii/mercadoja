-- =====================================================================
-- MercadoJá — DDL (PostgreSQL 14+)
-- Trabalho Prático de Banco de Dados II
-- =====================================================================
-- Convenções:
--   * chaves primárias: <entidade>_id BIGSERIAL / SERIAL
--   * datas de auditoria em timestamp, datas de negócio em date/timestamp
--     conforme granularidade exigida pelas perguntas de negócio
--   * nomes em snake_case, em português, no singular
-- =====================================================================

DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;

-- ---------------------------------------------------------------------
-- CLIENTE
-- ---------------------------------------------------------------------
CREATE TABLE cliente (
    cliente_id      BIGSERIAL PRIMARY KEY,
    nome            VARCHAR(120)  NOT NULL,
    email           VARCHAR(160)  NOT NULL UNIQUE,
    telefone        VARCHAR(20)   NOT NULL,
    cidade          VARCHAR(80)   NOT NULL,
    uf              CHAR(2)       NOT NULL,
    data_cadastro   DATE          NOT NULL,
    segmento        VARCHAR(20)   NOT NULL,
    CONSTRAINT chk_cliente_uf CHECK (uf ~ '^[A-Z]{2}$'),
    CONSTRAINT chk_cliente_segmento CHECK (segmento IN ('novo','regular','vip','inativo'))
);
COMMENT ON TABLE cliente IS 'Clientes do marketplace (endereço de cadastro; endereço de entrega vive em pedido, pois pode variar por pedido).';

-- ---------------------------------------------------------------------
-- LOJA (vendedor)
-- ---------------------------------------------------------------------
CREATE TABLE loja (
    loja_id           BIGSERIAL PRIMARY KEY,
    nome_fantasia     VARCHAR(120) NOT NULL,
    cnpj              CHAR(14)     NOT NULL UNIQUE,
    cidade            VARCHAR(80)  NOT NULL,
    uf                CHAR(2)      NOT NULL,
    plano_assinatura  VARCHAR(20)  NOT NULL,
    data_adesao       DATE         NOT NULL,
    ativa             BOOLEAN      NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_loja_uf CHECK (uf ~ '^[A-Z]{2}$'),
    CONSTRAINT chk_loja_plano CHECK (plano_assinatura IN ('gratis','basico','pro','enterprise'))
);
COMMENT ON TABLE loja IS 'Lojas parceiras (vendedores) do marketplace.';

-- ---------------------------------------------------------------------
-- CATEGORIA (hierarquia de 2 níveis: raiz -> filha)
-- ---------------------------------------------------------------------
CREATE TABLE categoria (
    categoria_id        SERIAL PRIMARY KEY,
    nome                VARCHAR(80) NOT NULL,
    categoria_pai_id    INT NULL REFERENCES categoria(categoria_id),
    CONSTRAINT uq_categoria_nome_pai UNIQUE (nome, categoria_pai_id)
);
COMMENT ON TABLE categoria IS 'categoria_pai_id NULL = categoria raiz (12 linhas); NOT NULL = categoria filha (39 linhas), aponta para uma raiz.';
-- Regra de negócio (não é possível expressar em CHECK simples sem função):
-- uma categoria filha não pode ter categoria_pai_id apontando para outra filha.
-- Validada no script de carga e documentada aqui.

-- ---------------------------------------------------------------------
-- PRODUTO
-- ---------------------------------------------------------------------
CREATE TABLE produto (
    produto_id      BIGSERIAL PRIMARY KEY,
    loja_id         BIGINT NOT NULL REFERENCES loja(loja_id),
    categoria_id    INT NOT NULL REFERENCES categoria(categoria_id),
    nome            VARCHAR(160) NOT NULL,
    descricao       TEXT,
    preco           NUMERIC(10,2) NOT NULL,
    estoque         INT NOT NULL DEFAULT 0,
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    data_criacao    TIMESTAMP NOT NULL,
    CONSTRAINT chk_produto_preco CHECK (preco > 0),
    CONSTRAINT chk_produto_estoque CHECK (estoque >= 0)
);
COMMENT ON TABLE produto IS 'Catálogo de produtos; cada produto pertence a uma loja e a uma categoria (idealmente folha).';

-- ---------------------------------------------------------------------
-- PEDIDO
-- ---------------------------------------------------------------------
CREATE TABLE pedido (
    pedido_id           BIGSERIAL PRIMARY KEY,
    cliente_id          BIGINT NOT NULL REFERENCES cliente(cliente_id),
    data_pedido         TIMESTAMP NOT NULL,
    status              VARCHAR(20) NOT NULL,
    canal_venda         VARCHAR(20) NOT NULL,
    cidade_entrega      VARCHAR(80) NOT NULL,
    uf_entrega          CHAR(2) NOT NULL,
    valor_produtos      NUMERIC(10,2) NOT NULL, -- soma de (qtd*preco_unit - desconto_item) dos itens; guardado no cabeçalho por performance (ver RELATORIO.pdf, seção de normalização)
    valor_frete         NUMERIC(10,2) NOT NULL,
    valor_desconto      NUMERIC(10,2) NOT NULL DEFAULT 0, -- desconto adicional a nível de pedido (cupom), distinto do desconto por item
    CONSTRAINT chk_pedido_status CHECK (status IN ('carrinho','pago','enviado','entregue','cancelado')),
    CONSTRAINT chk_pedido_canal CHECK (canal_venda IN ('aplicativo','site','whatsapp')),
    CONSTRAINT chk_pedido_uf CHECK (uf_entrega ~ '^[A-Z]{2}$'),
    CONSTRAINT chk_pedido_valores CHECK (valor_produtos >= 0 AND valor_frete >= 0 AND valor_desconto >= 0)
);
COMMENT ON TABLE pedido IS 'Cabeçalho do pedido. valor_produtos é denormalizado (cache) a partir de item_pedido para evitar agregação em toda leitura do painel comercial.';

-- ---------------------------------------------------------------------
-- ITEM_PEDIDO
-- ---------------------------------------------------------------------
CREATE TABLE item_pedido (
    item_pedido_id   BIGSERIAL PRIMARY KEY,
    pedido_id        BIGINT NOT NULL REFERENCES pedido(pedido_id),
    produto_id       BIGINT NOT NULL REFERENCES produto(produto_id),
    quantidade       INT NOT NULL,
    preco_unitario   NUMERIC(10,2) NOT NULL,
    desconto_item    NUMERIC(10,2) NOT NULL DEFAULT 0,
    CONSTRAINT chk_item_qtd CHECK (quantidade > 0),
    CONSTRAINT chk_item_preco CHECK (preco_unitario > 0),
    CONSTRAINT chk_item_desconto CHECK (desconto_item >= 0)
);
COMMENT ON TABLE item_pedido IS 'preco_unitario é copiado de produto.preco no momento da compra (histórico de preço, não deve ser FK de valor).';

-- ---------------------------------------------------------------------
-- PAGAMENTO
-- ---------------------------------------------------------------------
CREATE TABLE pagamento (
    pagamento_id     BIGSERIAL PRIMARY KEY,
    pedido_id        BIGINT NOT NULL REFERENCES pedido(pedido_id),
    metodo           VARCHAR(20) NOT NULL,
    status           VARCHAR(20) NOT NULL,
    valor            NUMERIC(10,2) NOT NULL,
    data_pagamento   TIMESTAMP,
    CONSTRAINT chk_pagamento_metodo CHECK (metodo IN ('pix','cartao_credito','cartao_debito','boleto','dinheiro')),
    CONSTRAINT chk_pagamento_status CHECK (status IN ('pendente','aprovado','recusado','estornado')),
    CONSTRAINT chk_pagamento_valor CHECK (valor >= 0)
);

-- ---------------------------------------------------------------------
-- ENTREGA
-- ---------------------------------------------------------------------
CREATE TABLE entrega (
    entrega_id        BIGSERIAL PRIMARY KEY,
    pedido_id         BIGINT NOT NULL REFERENCES pedido(pedido_id),
    transportadora    VARCHAR(80) NOT NULL,
    status            VARCHAR(20) NOT NULL,
    data_envio        TIMESTAMP,
    data_entrega      TIMESTAMP,
    custo_frete       NUMERIC(10,2) NOT NULL,
    CONSTRAINT chk_entrega_status CHECK (status IN ('preparando','enviado','em_transito','entregue','extraviado')),
    CONSTRAINT chk_entrega_custo CHECK (custo_frete >= 0),
    CONSTRAINT chk_entrega_datas CHECK (data_entrega IS NULL OR data_envio IS NULL OR data_entrega >= data_envio)
);

-- ---------------------------------------------------------------------
-- AVALIACAO
-- ---------------------------------------------------------------------
CREATE TABLE avaliacao (
    avaliacao_id     BIGSERIAL PRIMARY KEY,
    pedido_id        BIGINT NOT NULL REFERENCES pedido(pedido_id),
    produto_id       BIGINT NOT NULL REFERENCES produto(produto_id),
    cliente_id       BIGINT NOT NULL REFERENCES cliente(cliente_id),
    nota             SMALLINT NOT NULL,
    comentario       TEXT,
    data_avaliacao   TIMESTAMP NOT NULL,
    CONSTRAINT chk_avaliacao_nota CHECK (nota BETWEEN 1 AND 5)
);

-- =====================================================================
-- Índices de apoio à integridade referencial (FKs não geram índice
-- automático no Postgres, exceto na tabela "de dentro" da FK — os
-- índices de PERFORMANCE ficam em sql/indices.sql, criados só depois
-- da medição da linha de base, conforme o protocolo do enunciado)
-- =====================================================================
