# Conformidade com o contrato de dados

## Entidade × linhas geradas × mínimo pedido
(Confirmado na carga real do aluno, banco Neon, `--scale 1.0`)

| Entidade | Mínimo do contrato | Linhas geradas | Atende? |
|---|---:|---:|---|
| Cliente | 100.000 | 100.000 | ✅ |
| Loja | 5.000 | 5.000 | ✅ |
| Categoria | 51 (12 raízes + 39 filhas) | 51 (12 + 39) | ✅ |
| Produto | 40.000 | 40.000 | ✅ |
| Pedido | 600.000 | 600.000 | ✅ |
| Item de pedido | 1.500.000 | 1.579.193 | ✅ |
| Pagamento | 400.000 | 492.273 | ✅ |
| Entrega | 400.000 | 432.122 | ✅ |
| Avaliação | 250.000 | 250.000 | ✅ |

## Distribuições obrigatórias × medido
(Consulta de conferência rodada diretamente no banco Neon do aluno)

| Regra do contrato | Alvo | Medido no banco do aluno |
|---|---|---|
| Pedidos faturados (pago/enviado/entregue) | ≥ 70% | 82,0% (47,1% entregue + 24,9% enviado + 10,0% pago) |
| Pedidos cancelados | 12% a 16% | 14,0% |
| Pedidos em carrinho (abandono, não contabilizado no contrato) | — | 4,0% |
| Itens por pedido (média) | ~2,5 | ~2,6 |

> A seed do gerador é fixa (`SEED = 20260915`), então a distribuição de
> status veio **idêntica** — dígito a dígito — tanto no ambiente de
> desenvolvimento quanto no banco de produção do aluno no Neon,
> confirmando que a carga é determinística e reproduzível em qualquer
> ambiente, como exige a seção "Armadilha comum" do enunciado.

## Declaração de uso de assistentes de IA
Claude (Anthropic) foi usado como ferramenta de estudo, escrita de
SQL/Python, e para orientar e validar a execução completa do pipeline —
incluindo a carga do volume total do contrato, a execução das 9
consultas de negócio, a otimização da consulta legada e as Análises
A1–A6 — diretamente no banco de produção do aluno (Neon).

**Nota de transparência sobre a Análise A5 (custo de escrita):** não foi
possível concluir essa medição especificamente ao vivo no banco do aluno
devido a uma limitação de armazenamento do plano gratuito do Neon (512
MB), atingida mesmo para operações mínimas de teste. Seis tentativas de
contorno foram feitas e documentadas (ver `evidencias/a5_custo_escrita.txt`
e a seção 5 do `RELATORIO.docx`); os números finais usados para essa
análise específica vêm de um ambiente de validação equivalente (mesma
estrutura de tabela, mesmo volume completo do contrato), não do banco
de produção do aluno. Todas as outras oito consultas, a consulta legada,
e as Análises A1, A2, A3, A4 e A6 têm evidência 100% própria, medida
diretamente no banco do aluno.
