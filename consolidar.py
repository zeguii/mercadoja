import re, os

def parse_resumo(caminho):
    dados = {}
    for linha in open(caminho, encoding="utf-8"):
        m = re.match(r"(\S+)\s+execucoes=(\[.*?\])\s+mediana=([\d.]+) ms\s+blocos=(\d+)", linha)
        if m:
            nome, execs, mediana, blocos = m.groups()
            dados[nome] = (execs, float(mediana), int(blocos))
    return dados

antes = parse_resumo("evidencias/resumo_antes.txt")
depois = parse_resumo("evidencias/resumo_depois.txt")

pares = [("q1","q1"),("q2","q2"),("q3","q3"),("q4","q4"),("q5","q5"),
         ("q6","q6"),("q7","q7"),("q8","q8"),("q9","q9"),
         ("legado_antes","legado_depois")]

linhas_md = ["| Consulta | Mediana antes (ms) | Mediana depois (ms) | Ganho % | Blocos antes | Blocos depois |",
             "|---|---:|---:|---:|---:|---:|"]

for a, d in pares:
    execs_a, med_a, blk_a = antes[a]
    execs_d, med_d, blk_d = depois[d]
    ganho = (med_a - med_d) / med_a * 100
    nome_pasta = "legado" if a == "legado_antes" else a
    linhas_md.append(f"| {nome_pasta} | {med_a:.1f} | {med_d:.1f} | {ganho:.1f}% | {blk_a} | {blk_d} |")

    pasta = f"evidencias/{nome_pasta}"
    os.makedirs(pasta, exist_ok=True)
    with open(f"evidencias/antes/{a}.txt", encoding="utf-8") as f:
        antes_txt = f.read()
    with open(f"evidencias/depois/{d}.txt", encoding="utf-8") as f:
        depois_txt = f.read()
    open(f"{pasta}/antes.txt", "w", encoding="utf-8").write(antes_txt)
    open(f"{pasta}/depois.txt", "w", encoding="utf-8").write(depois_txt)
    with open(f"{pasta}/resumo.md", "w", encoding="utf-8") as f:
        f.write(f"# Resumo — {nome_pasta}\n\n")
        f.write(f"- Execuções ANTES: {execs_a} -> mediana {med_a:.1f} ms\n")
        f.write(f"- Execuções DEPOIS: {execs_d} -> mediana {med_d:.1f} ms\n")
        f.write(f"- Ganho: {ganho:.1f}%\n")
        f.write(f"- Blocos lidos ANTES: {blk_a}\n")
        f.write(f"- Blocos lidos DEPOIS: {blk_d}\n")

with open("evidencias/RESUMO_GERAL.md", "w", encoding="utf-8") as f:
    f.write("# Resumo geral — antes x depois (3 execuções, mediana)\n\n")
    f.write("\n".join(linhas_md))
    f.write("\n")

print("\n".join(linhas_md))
