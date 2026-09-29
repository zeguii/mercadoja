# Modelo Relacional — MercadoJá

## Entidades e relacionamentos (cardinalidade)

- **Cliente** (1) — (N) **Pedido**
- **Loja** (1) — (N) **Produto**
- **Categoria** (1, raiz) — (N) **Categoria** (filha) — auto-relacionamento via `categoria_pai_id`
- **Categoria** (1) — (N) **Produto**
- **Pedido** (1) — (N) **ItemPedido** (N) — (1) **Produto**
- **Pedido** (1) — (N) **Pagamento**
- **Pedido** (1) — (N) **Entrega** (na prática 0 ou 1 por pedido, mas modelado 1:N para permitir reenvio)
- **Pedido** (1) — (N) **Avaliação**, **Produto** (1) — (N) **Avaliação**, **Cliente** (1) — (N) **Avaliação**

Diagrama textual (entidade → chaves estrangeiras):

```
cliente ──< pedido >── item_pedido >── produto >── loja
                │                         │
                │                         └──> categoria (auto-FK: categoria_pai_id)
                ├──< pagamento
                ├──< entrega
                └──< avaliacao >── produto, cliente
```

> Para o entregável `modelo/der.png`, exporte este mesmo diagrama de um
> editor ER (dbdiagram.io, drawio ou pgAdmin ERD) a partir do `sql/ddl.sql`.

## Justificativa de 3ª Forma Normal (3FN)

O ponto de partida ingênuo seria uma única tabela larga "pedido" com nome
do cliente, nome do produto, nome da loja etc. repetidos em cada linha.
Isso viola 2FN/3FN porque atributos como `cliente.nome` dependem só de
`cliente_id`, não da chave completa do pedido — e ficariam redundantes
a cada novo pedido do mesmo cliente. Decisões de normalização tomadas:

1. **Cliente separado de Pedido.** `nome`, `email`, `cidade` do cliente
   dependem só de `cliente_id`. Ficar junto do pedido geraria anomalia de
   atualização (mudar o e-mail do cliente exigiria atualizar N linhas).

2. **Produto separado de Loja e de Categoria.** `preco` e `estoque`
   dependem de `produto_id`, não do pedido. Repeti-los por item de pedido
   seria redundante — por isso `item_pedido` guarda apenas
   `preco_unitario` (histórico do preço no momento da compra, uma cópia
   INTENCIONAL, não uma violação: é um fato sobre a venda, não sobre o
   produto atual).

3. **Categoria com auto-relacionamento (raiz/filha) em vez de duas
   tabelas (`categoria_raiz`, `categoria_filha`).** Uma tabela só com
   `categoria_pai_id` nulo para raízes evita duplicar a estrutura de
   colunas e ainda modela corretamente uma hierarquia de exatamente 2
   níveis (a introdução de mais um nível não quebraria o esquema).

4. **item_pedido como tabela associativa** entre `pedido` e `produto`,
   pois a relação é N:N (um pedido tem vários produtos, um produto
   aparece em vários pedidos) e carrega atributos próprios da associação
   (`quantidade`, `desconto_item`) que não pertencem nem a pedido nem a
   produto isoladamente — exatamente o caso clássico que exige uma
   tabela associativa em 3FN.

5. **Pagamento e Entrega como tabelas separadas de Pedido**, mesmo
   podendo (na prática desta operação) ter cardinalidade quase 1:1 com
   pedido. Motivo: são eventos com seu próprio ciclo de vida (podem não
   existir ainda, podem ser reemitidos/reenviados) e atributos que não
   fazem sentido como colunas de `pedido` (ex.: múltiplas tentativas de
   pagamento por pedido).

### Denormalização intencional (e por quê)

`pedido.valor_produtos`, `pedido.valor_frete` e `pedido.valor_desconto`
SÃO redundantes em relação ao que se poderia recalcular agregando
`item_pedido` — mas o contrato de dados do enunciado pede esses campos
explicitamente no cabeçalho do pedido, e o painel comercial (Q4) e o
relatório da diretoria (Q1) fazem essa agregação em quase toda consulta
analítica. Guardar o total já calculado no cabeçalho evita reagregar
1,58 milhão de linhas de `item_pedido` toda vez que alguém quer só o
ticket médio. O preço é manter a consistência via aplicação (ou trigger)
no momento da escrita — trade-off clássico de modelagem OLTP com leitura
analítica pesada, e deve ser citado no RELATORIO.pdf como decisão
consciente, não como erro de normalização.
