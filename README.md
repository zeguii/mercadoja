# MercadoJá — Trabalho Prático de Banco de Dados II

## SGBD e versão usada nas medições
PostgreSQL **18** via [Neon](https://neon.tech) (serviço gratuito na nuvem).
O enunciado aceita 14+ e permite explicitamente "instalação local (Docker
ou nativa) ou serviço gratuito" — optamos pelo Neon por ser a opção mais
rápida de configurar sem depender de instalação local (Docker Desktop
teria exigido WSL2 no Windows).

## Como subir o banco do zero (Neon)

1. Crie uma conta gratuita em https://neon.tech e um projeto novo.
2. No painel do projeto, clique em **Connect** e copie a *connection
   string* (formato `postgresql://usuario:senha@ep-xxxx.neon.tech/dbname?sslmode=require`).
   **Nunca commite essa string no Git** — ela contém a senha do banco.
3. Instale a dependência Python:
   ```
   pip install psycopg2-binary
   ```
4. Rode o DDL (cria as tabelas):
   ```python
   import psycopg2
   conn = psycopg2.connect("SUA_CONNECTION_STRING")
   cur = conn.cursor()
   cur.execute(open("sql/ddl.sql", encoding="utf-8").read())
   conn.commit()
   ```
5. Carregue o volume completo do contrato:
   ```
   python sql/dados/gerar_dados.py --scale 1.0 --dsn "SUA_CONNECTION_STRING"
   ```
6. Aplique os índices de performance:
   ```python
   cur.execute(open("sql/indices.sql", encoding="utf-8").read())
   conn.commit()
   ```

### Alternativas equivalentes (não usadas aqui, mas válidas)
- **Docker**: `docker run --name mercadoja-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=mercadoja -p 5432:5432 -d postgres:16`, depois aplicar `ddl.sql` e o gerador apontando para `localhost`.
- **Instalação nativa**: instalador oficial do PostgreSQL para o seu sistema operacional.

## Parâmetro `--scale`
- `--scale 1.0` → volume cheio do contrato (usado na entrega final).
- A seed é fixa (`SEED = 20260915` em `sql/dados/gerar_dados.py`), então
  a mesma escala sempre reproduz os mesmos dados, linha por linha — **em
  qualquer máquina ou serviço**. Confirmamos isso na prática: a
  distribuição de status dos pedidos veio idêntica (cancelado 14,0%,
  entregue 47,1%, enviado 24,9%, pago 10,0%, carrinho 4,0%) tanto no
  ambiente de desenvolvimento quanto no Neon do aluno.

## Contagem de linhas obtida (confirmada na carga real do aluno, Neon)

| Tabela | Linhas geradas | Mínimo do contrato |
|---|---:|---:|
| cliente | 100.000 | 100.000 |
| loja | 5.000 | 5.000 |
| categoria | 51 | 51 |
| produto | 40.000 | 40.000 |
| pedido | 600.000 | 600.000 |
| item_pedido | 1.579.193 | 1.500.000 |
| pagamento | 492.273 | 400.000 |
| entrega | 432.122 | 400.000 |
| avaliacao | 250.000 | 250.000 |

## Ordem de execução (a que foi seguida de fato nesta entrega)
1. `sql/ddl.sql`
2. `sql/dados/gerar_dados.py --scale 1.0`
3. Conferência de volumes e proporções (ver `CONFORMIDADE.md`)
4. Medição da linha de base: cada `sql/qN.sql` e `sql/legado_antes.sql`
   com `EXPLAIN (ANALYZE, BUFFERS)`, 3 execuções cada, mediana — salvo em
   `evidencias/antes/` e consolidado em `evidencias/resumo_antes.txt`.
5. `sql/indices.sql`
6. Medição pós-índice (mesmo processo) — `evidencias/depois/` e
   `evidencias/resumo_depois.txt`.
7. Conferência de que `legado_antes.sql` e `legado_depois.sql` devolvem
   resultado idêntico (`Compare-Object` no PowerShell — zero diferenças).
8. Análises A3 (reescrita da Q7 sem índice), A4 (contraprova de
   seletividade) e A6 (índice redundante) — todas medidas ao vivo no
   banco do aluno. A5 (custo de escrita) não pôde ser concluída ao vivo
   por uma limitação de armazenamento do plano gratuito do Neon — ver
   `evidencias/a5_custo_escrita.txt` para o relato completo das
   tentativas e os números de referência usados no lugar.

### Scripts de medição usados (Python, não bash — ambiente Windows)
Os scripts `medir.py`, `rodar.py`, `a3_teste.py`, `a4_contraprova.py`,
`a6_redundante_v2.py` e `consolidar.py`, usados para gerar as evidências
desta entrega, estão descritos passo a passo no histórico de
desenvolvimento; a lógica de cada um está comentada no próprio arquivo
gerado (ver pasta raiz do projeto). Eles fazem essencialmente:
`EXPLAIN (ANALYZE, BUFFERS)` de um arquivo `.sql`, salvando tempo de
execução e blocos lidos em `evidencias/`.

## Uso de assistentes de IA (declaração exigida pelo enunciado)
Claude (Anthropic) foi usado para: desenhar o modelo relacional e a
justificativa de 3FN; escrever o DDL; escrever o gerador de dados
sintéticos; escrever as 9 consultas de negócio e a reescrita da consulta
legada; escrever e justificar os índices; escrever os scripts Python de
medição (`medir.py`, `rodar.py` etc.) adaptados ao ambiente Windows do
aluno; e orientar passo a passo a execução real de todo o pipeline no
banco de produção do aluno (Neon) — incluindo o diagnóstico e contorno
de um problema real de limite de armazenamento do plano gratuito durante
a Análise A5. Cada decisão de índice e cada reescrita têm comentário de
"por quê" junto ao SQL — releia antes de defender o trabalho, pois a
banca pode pedir reprodução ao vivo de qualquer linha ou número.

## O que ainda precisa ser feito
- `modelo/der.png` — exportar um diagrama ER visual (dbdiagram.io,
  drawio ou o ERD do pgAdmin) a partir de `sql/ddl.sql` ou
  `modelo/modelo_relacional.md`.
- Commits ao longo do processo no Git (a rubrica avalia versionamento
  visível, não um commit único no final).
- Resetar a senha do banco no Neon antes da entrega final, caso a
  connection string tenha sido exposta em algum momento durante o
  desenvolvimento (boa prática de segurança, não afeta a nota).
