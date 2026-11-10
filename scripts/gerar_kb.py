"""Valida respostas.yaml, gera site/kb.json e publica as Centrais (pasta centrais/).

Uso:  python scripts/gerar_kb.py respostas.yaml site
Roda sozinho no GitHub (aba Actions) a cada alteração do respostas.yaml.
Se encontrar erro, para com uma mensagem explicando o que corrigir e NADA é publicado.

Centrais: todo arquivo .html dentro da pasta centrais/ é publicado no mesmo endereço,
ex.: centrais/central-comissoes.html -> https://<usuario>.github.io/w1-assistente-comissoes/central-comissoes.html
Arquivos sem <!DOCTYPE>/<head> (formato exportado do Claude) recebem o cabeçalho automaticamente.
"""
import json
import re
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import yaml

NOINDEX = '<meta name="robots" content="noindex, nofollow">'
PROIBIDOS_PUBLICO = ("admin",)   # arquivos com estes termos no nome nunca são publicados

TAGS_OK = {"p", "ul", "ol", "li", "strong", "em", "b", "i", "br", "a", "table", "thead", "tbody",
           "tr", "th", "td", "span", "h4", "div"}
ATTRS_OK = {"class", "href", "target", "rel"}
SECOES = {
    "comissoes": {"calendario", "w1nner", "prazos", "fup", "bonus", "realocacao", "calculadora-pps",
                  "outros", "ticket", "academy", "regras-ap", "regras-fup", "produtos-financeiros"},
    "estornos": {"conceitos", "resumo", "calculadora", "icatu", "mag", "sulamerica", "prudential", "amil",
                 "saudemais", "vilavelha", "itau", "cnp", "embracon", "magalu", "bb", "duvidas"},
}


class Checker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.problemas = []

    def handle_starttag(self, tag, attrs):
        if tag not in TAGS_OK:
            self.problemas.append(f"tag <{tag}> não é permitida")
        for nome, valor in attrs:
            if nome not in ATTRS_OK:
                self.problemas.append(f"atributo '{nome}' não é permitido (em <{tag}>)")
            if nome == "href" and not re.match(r"^https?://", valor or ""):
                self.problemas.append(f"link precisa começar com https:// ({valor})")


def falhar(erros):
    print("\n❌ A publicação foi interrompida. Corrija no respostas.yaml:\n")
    for e in erros:
        print("  •", e)
    print("\nOs consultores continuam com a versão anterior até a correção.")
    sys.exit(1)


def main(origem, destino):
    try:
        doc = yaml.safe_load(Path(origem).read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        marca = getattr(e, "problem_mark", None)
        onde = f" (perto da linha {marca.line + 1})" if marca else ""
        falhar([f"o arquivo não está no formato certo{onde}. Confira a indentação e os dois-pontos. Detalhe: {e}"])

    erros = []
    parceiras = doc.get("parceiras") or {}
    respostas = doc.get("respostas") or []
    if not isinstance(respostas, list) or len(respostas) < 10:
        falhar(["a lista 'respostas' está vazia ou com menos de 10 itens"])

    vistos, itens = set(), []
    for n, r in enumerate(respostas, 1):
        ref = f"resposta nº {n} (id: {r.get('id', '?')})" if isinstance(r, dict) else f"resposta nº {n}"
        if not isinstance(r, dict):
            erros.append(f"{ref}: formato inválido")
            continue
        for campo in ("id", "area", "pergunta", "resposta", "secao"):
            if not str(r.get(campo) or "").strip():
                erros.append(f"{ref}: falta o campo '{campo}'")
        rid = str(r.get("id") or "").strip()
        if rid in vistos:
            erros.append(f"{ref}: o id '{rid}' está repetido")
        vistos.add(rid)
        area = r.get("area")
        if area not in ("comissoes", "estornos"):
            erros.append(f"{ref}: 'area' deve ser comissoes ou estornos (está '{area}')")
        parc = r.get("parceira") or ""
        if parc and parc not in parceiras:
            erros.append(f"{ref}: parceira '{parc}' não está na lista 'parceiras'")
        secao = str(r.get("secao") or "")
        pag, _, sec = secao.partition("#")
        if pag not in SECOES or sec not in SECOES[pag]:
            erros.append(f"{ref}: secao '{secao}' não existe. Use, por exemplo, comissoes#prazos ou estornos#icatu")
        html = str(r.get("resposta") or "")
        chk = Checker()
        chk.feed(html)
        erros += [f"{ref}: {p}" for p in chk.problemas]
        alt = r.get("outras_formas") or []
        if isinstance(alt, str):
            alt = [alt]
        itens.append({
            "id": rid,
            "cat": "c" if area == "comissoes" else "e",
            "p": parc,
            "q": str(r.get("pergunta") or "").strip(),
            "alt": [str(a) for a in alt],
            "tags": str(r.get("palavras_chave") or ""),
            "a": html.strip(),
            "link": secao,
        })
    if erros:
        falhar(erros)

    def registro(r):
        """Endereço do Apps Script que guarda as perguntas (só aceita script.google.com)."""
        url = str(r.get("url") or "").strip()
        if url and not re.match(r"^https://script\.google\.com/macros/s/[\w-]+/exec$", url):
            falhar([f"registro.url inválido: {url} (use o endereço do App da Web, terminando em /exec)"])
        return {"url": url if r.get("ativo", True) else ""}

    regras = carregar_regras(Path(origem).parent / "regras.yaml")

    ext = doc.get("extensao") or {}
    kb = {
        "versao": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated": str(doc.get("atualizado_em") or ""),
        "extensao": {"versao": str(ext.get("versao") or ""), "aviso": str(ext.get("aviso") or "")},
        "registro": registro(doc.get("registro") or {}),
        "partners": {str(k): str(v) for k, v in parceiras.items()},
        "items": itens,
        "regras": regras,
    }
    out = Path(destino)
    out.mkdir(parents=True, exist_ok=True)
    centrais = publicar_centrais(Path(origem).parent / "centrais", out)
    pdfs = publicar_docs(Path(origem).parent / "centrais" / "docs", out / "docs")
    (out / "kb.json").write_text(json.dumps(kb, ensure_ascii=False), encoding="utf-8")
    (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    links = "".join(f'<li><a href="{n}">{n}</a></li>' for n in centrais)
    (out / "index.html").write_text(
        f'<!doctype html><meta charset="utf-8">{NOINDEX}'
        f"<title>FAQ Comissões W1</title><p>Base do FAQ Comissões W1 · {len(itens)} respostas · "
        f"publicada em {kb['versao']}</p>" + (f"<p>Centrais publicadas:</p><ul>{links}</ul>" if links else ""), encoding="utf-8")
    print(f"✅ {len(itens)} respostas validadas e publicadas (versão {kb['versao']}).")
    for n in centrais:
        print(f"✅ Central publicada: {n}")
    for n in pdfs:
        print(f"✅ Documento publicado: docs/{n}")


def carregar_regras(arq):
    """Lê o regras.yaml (tabelas oficiais usadas nos cálculos do balão e da Central)."""
    if not arq.exists():
        return None
    try:
        r = yaml.safe_load(arq.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        falhar([f"o regras.yaml não está no formato certo. Detalhe: {e}"])
    erros = []
    for chave in ("docs", "cargos", "bonus", "ap", "fup"):
        if not r.get(chave):
            erros.append(f"regras.yaml: falta a seção '{chave}'")
    for k, d in (r.get("docs") or {}).items():
        if not str(d.get("titulo", "")).strip():
            erros.append(f"regras.yaml: o documento '{k}' precisa de um titulo")
    ids = {c.get("id") for c in r.get("cargos") or []}
    for c in ("fa1", "fa2", "fa3", "fa4", "p", "sp", "ap", "pr", "mp", "mob"):
        if c not in ids:
            erros.append(f"regras.yaml: falta o cargo '{c}' na lista cargos")
    if erros:
        falhar(erros)
    return r


def publicar_docs(pasta, out):
    """Desativado: os documentos oficiais ficam só no W1nner (Arquivos › Comissões).
    Mesmo que alguém suba PDFs na pasta centrais/docs, eles NÃO são publicados."""
    nomes = []
    if True:
        return nomes
    out.mkdir(parents=True, exist_ok=True)
    for arq in sorted(pasta.glob("*.pdf")):
        if any(p in arq.name.lower() for p in PROIBIDOS_PUBLICO):
            continue
        (out / arq.name).write_bytes(arq.read_bytes())
        nomes.append(arq.name)
    return nomes


def publicar_centrais(pasta, out):
    """Copia as Centrais (HTML) para o site, completando o cabeçalho quando faltar."""
    nomes = []
    if not pasta.is_dir():
        return nomes
    for arq in sorted(pasta.glob("*.html")):
        if any(p in arq.name.lower() for p in PROIBIDOS_PUBLICO):
            print(f"⚠️  {arq.name} NÃO foi publicado (arquivo interno/admin).")
            continue
        html = arq.read_text(encoding="utf-8")
        if not html.lstrip()[:15].lower().startswith("<!doctype"):
            html = ('<!DOCTYPE html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n'
                    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                    f"{NOINDEX}\n</head>\n<body>\n{html}\n</body>\n</html>\n")
        elif "noindex" not in html.lower():
            html = re.sub(r"(<head[^>]*>)", r"\1\n" + NOINDEX, html, count=1, flags=re.I)
        nome = arq.name.lower()
        for a, b in (("á", "a"), ("à", "a"), ("ã", "a"), ("â", "a"), ("é", "e"), ("ê", "e"), ("í", "i"),
                     ("ó", "o"), ("õ", "o"), ("ô", "o"), ("ú", "u"), ("ç", "c")):
            nome = nome.replace(a, b)
        nome = re.sub(r"[^a-z0-9._-]+", "-", nome)
        (out / nome).write_text(html, encoding="utf-8")
        nomes.append(nome)
    return nomes


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "respostas.yaml", sys.argv[2] if len(sys.argv) > 2 else "site")
