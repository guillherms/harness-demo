#!/usr/bin/env python3
"""
parse_ldm.py — Converte um modelo lógico do PowerDesigner (.ldm salvo em XML)
numa base de conhecimento legível por agentes:

  <out>/
    _meta.md        origem, hash, data do parse, contagens
    _last-diff.md   o que mudou em relação ao parse anterior
    index.md        catálogo: diagramas e tabelas (1 linha cada)
    catalog.json    versão estruturada (usada pelo diff e por validadores)
    diagrams/<DIAGRAMA>.md
    tables/<TABELA>.md

Uso:
  python parse_ldm.py modelo.ldm --out docs/data-model
  python parse_ldm.py modelo.ldm --out docs/data-model --dry-run   # só mostra o diff

Somente stdlib (Python 3.9+). Saída determinística (ordenada) para diffs limpos no git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET

GENERATOR = "ldm-sync/parse_ldm.py v1"

# PowerDesigner declara xmlns:a="attribute" xmlns:c="collection" xmlns:o="object"
NS = {"attribute": "a", "collection": "c", "object": "o"}

WARNINGS: list[str] = []


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# ---------------------------------------------------------------- helpers XML
def tag(el: ET.Element) -> str:
    t = el.tag
    if isinstance(t, str) and t.startswith("{"):
        uri, local = t[1:].split("}", 1)
        return f"{NS.get(uri, uri)}:{local}"
    return t if isinstance(t, str) else ""


def child(el: ET.Element, name: str) -> ET.Element | None:
    for c in el:
        if tag(c) == name:
            return c
    return None


def text(el: ET.Element, name: str) -> str:
    c = child(el, name)
    return (c.text or "").strip() if c is not None and c.text else ""


def refs(el: ET.Element, collection: str) -> list[str]:
    c = child(el, collection)
    if c is None:
        return []
    return [x.get("Ref") for x in c if x.get("Ref")]


def to_iso(epoch: str) -> str:
    try:
        return datetime.fromtimestamp(int(epoch), tz=timezone.utc).strftime("%Y-%m-%d")
    except (ValueError, OSError, OverflowError):
        return ""


# ------------------------------------------------- atributos estendidos / comment
EXT_RE = re.compile(r"\{([0-9A-Fa-f-]{36})\},([^,\r\n]*),(\d+)=")


def parse_extended(s: str) -> dict[str, str]:
    """Formato PowerDesigner: {GUID},Nome,<tamanho>=valor — pode ser aninhado
    (extensão > atributos). Tolerante a desvios de tamanho por normalização de \\r\\n."""
    out: dict[str, str] = {}
    i = 0
    while True:
        m = EXT_RE.search(s, i)
        if not m:
            break
        name, n, start = m.group(2).strip(), int(m.group(3)), m.end()
        val = s[start:start + n]
        i = start + n
        if EXT_RE.match(val.lstrip()):
            # container (extensão): se o tamanho veio "inflado" pela normalização de
            # \r\n, o slice já inclui os próximos atributos e a recursão os lê
            out.update(parse_extended(val))
        else:
            # valor-folha não pode conter o início do próximo atributo
            nxt = EXT_RE.search(val)
            if nxt:
                val, i = val[:nxt.start()], start + nxt.start()
            out[name] = val.strip()
    return out


COMMENT_FIELD_RE = re.compile(r"^\s*([A-Za-zÀ-ÿ][^:\n]{1,50}?):\s*(.+?)\s*$")


def parse_comment_fields(comment: str) -> dict[str, str]:
    """Extrai linhas no padrão 'Rótulo: valor' (ex.: 'Localização no arquivo: Header')."""
    fields: dict[str, str] = {}
    for line in comment.splitlines():
        m = COMMENT_FIELD_RE.match(line)
        if m and "://" not in line:
            fields[m.group(1).strip()] = m.group(2)
    return fields


# ------------------------------------------------------------------- parse
def load_root(path: Path) -> ET.Element:
    raw = path.read_bytes()
    if b"<?xml" not in raw[:300] and b"<Model" not in raw[:2000]:
        sys.exit(
            "ERRO: o arquivo não parece XML. No PowerDesigner, salve o modelo no "
            "formato XML (não binário) e rode de novo."
        )
    try:
        return ET.fromstring(raw)
    except ET.ParseError as e:
        sys.exit(f"ERRO: XML inválido ({e}).")


def parse_model(path: Path) -> dict:
    root = load_root(path)

    objs: dict[str, tuple[str, ET.Element, list[str]]] = {}

    def walk(el: ET.Element, pkg: list[str]) -> None:
        t = tag(el)
        if el.get("Id"):
            if t == "o:Package":
                pkg = pkg + [text(el, "a:Name") or text(el, "a:Code")]
            objs[el.get("Id")] = (t, el, pkg)
        for c in el:
            walk(c, pkg)

    walk(root, [])

    by_type: dict[str, list[str]] = {}
    for oid, (t, _, _) in objs.items():
        by_type.setdefault(t, []).append(oid)

    model_el = next((objs[i][1] for i in by_type.get("o:Model", [])), None)
    model = {
        "name": text(model_el, "a:Name") if model_el is not None else path.stem,
        "code": text(model_el, "a:Code") if model_el is not None else path.stem,
    }

    last_mod = max(
        (int(text(e, "a:ModificationDate") or 0) for _, e, _ in objs.values()),
        default=0,
    )

    # Domínios
    domains = {}
    for did in by_type.get("o:Domain", []):
        d = objs[did][1]
        domains[did] = {
            "code": text(d, "a:Code"),
            "datatype": text(d, "a:DataType"),
            "length": text(d, "a:Length"),
            "precision": text(d, "a:Precision"),
        }

    # Mapa ObjectID -> Id (para resolver atalhos/shortcuts)
    objid_to_id = {}
    for oid, (_, e, _) in objs.items():
        o = text(e, "a:ObjectID")
        if o:
            objid_to_id[o] = oid

    def resolve_entity(ref: str) -> str | None:
        """Retorna Id de entidade local, 'EXT:<code>' para atalho externo, ou None."""
        if ref not in objs:
            return None
        t, e, _ = objs[ref]
        if t == "o:Entity":
            return ref
        if t == "o:Shortcut":
            target = objid_to_id.get(text(e, "a:TargetID"))
            if target and objs[target][0] == "o:Entity":
                return target
            return "EXT:" + (text(e, "a:Code") or text(e, "a:Name") or ref)
        return None

    # Entidades
    entities: dict[str, dict] = {}
    attr_owner: dict[str, tuple[str, str]] = {}  # attrId -> (entityId, attrCode)

    for eid in by_type.get("o:Entity", []):
        _, e, pkg = objs[eid]
        code = text(e, "a:Code") or text(e, "a:Name") or eid
        ent = {
            "id": eid,
            "name": text(e, "a:Name"),
            "code": code,
            "comment": text(e, "a:Comment"),
            "package": "/".join(p for p in pkg if p),
            "columns": {},
            "column_order": [],
            "identifiers": [],
            "primary_key": [],
            "diagrams": [],
            "relationships": [],
            "_parent_refs": {},
        }
        attrs_c = child(e, "c:Attributes")
        for a in (attrs_c if attrs_c is not None else []):
            if tag(a) != "o:EntityAttribute" or not a.get("Id"):
                continue
            dom = refs(a, "c:Domain")
            d = domains.get(dom[0]) if dom else None
            acode = text(a, "a:Code") or text(a, "a:Name") or a.get("Id")
            comment = text(a, "a:Comment")
            ext_raw = text(a, "a:ExtendedAttributesText")
            try:
                ext = parse_extended(ext_raw) if ext_raw else {}
            except Exception:  # noqa: BLE001 — extended é "best effort"
                ext = {}
                warn(f"{code}.{acode}: não consegui ler ExtendedAttributesText")
            parents = []
            for c in a:
                ct = tag(c)
                if ct.startswith("c:") and ct != "c:Domain":
                    parents += [x.get("Ref") for x in c
                                if tag(x) == "o:EntityAttribute" and x.get("Ref")]
            col = {
                "name": text(a, "a:Name"),
                "code": acode,
                "datatype": text(a, "a:DataType") or (d or {}).get("datatype", ""),
                "length": text(a, "a:Length") or (d or {}).get("length", ""),
                "precision": text(a, "a:Precision") or (d or {}).get("precision", ""),
                "mandatory": text(a, "a:LogicalAttribute.Mandatory") == "1"
                or text(a, "a:Mandatory") == "1",
                "domain": (d or {}).get("code", ""),
                "migrated": text(a, "a:AutoMigrated") == "1",
                "pk": False,
                "fk": [],
                "comment": comment,
                "comment_fields": parse_comment_fields(comment),
                "extended": ext,
            }
            if not col["datatype"]:
                warn(f"{code}.{acode}: sem tipo de dado")
            if acode in ent["columns"]:
                warn(f"{code}: coluna duplicada {acode}")
            ent["columns"][acode] = col
            ent["column_order"].append(acode)
            ent["_parent_refs"][acode] = parents
            attr_owner[a.get("Id")] = (eid, acode)

        # Identificadores / PK
        primary = set(refs(e, "c:PrimaryIdentifier"))
        idents_c = child(e, "c:Identifiers")
        for idf in (idents_c if idents_c is not None else []):
            if tag(idf) != "o:Identifier" or not idf.get("Id"):
                continue
            cols = []
            for c in idf:
                if tag(c).startswith("c:"):
                    cols += [x.get("Ref") for x in c if tag(x) == "o:EntityAttribute"]
            ent["identifiers"].append({
                "id": idf.get("Id"),
                "name": text(idf, "a:Name"),
                "code": text(idf, "a:Code"),
                "primary": idf.get("Id") in primary,
                "_attr_refs": [r for r in cols if r],
            })
        entities[eid] = ent

    # Resolve PK e FK (precisa de todos os atributos indexados)
    for ent in entities.values():
        for idf in ent["identifiers"]:
            idf["columns"] = [attr_owner[r][1] for r in idf.pop("_attr_refs") if r in attr_owner]
            if idf["primary"]:
                ent["primary_key"] = idf["columns"]
                for c in idf["columns"]:
                    if c in ent["columns"]:
                        ent["columns"][c]["pk"] = True
        for acode, prefs in ent.pop("_parent_refs").items():
            for r in prefs:
                if r in attr_owner:
                    pe, pc = attr_owner[r]
                    ent["columns"][acode]["fk"].append(f"{entities[pe]['code']}.{pc}")

    # Relacionamentos
    relationships = []
    for rid in by_type.get("o:Relationship", []):
        r = objs[rid][1]
        o1, o2 = refs(r, "c:Object1"), refs(r, "c:Object2")
        e1 = resolve_entity(o1[0]) if o1 else None
        e2 = resolve_entity(o2[0]) if o2 else None
        if not e1 or not e2:
            warn(f"Relacionamento {text(r, 'a:Code') or rid}: extremidade não resolvida")
            continue
        rel = {
            "id": rid,
            "name": text(r, "a:Name"),
            "code": text(r, "a:Code"),
            "entity1": e1,
            "entity2": e2,
            "card_1_to_2": text(r, "a:Entity1ToEntity2RoleCardinality"),
            "card_2_to_1": text(r, "a:Entity2ToEntity1RoleCardinality"),
            "role_1_to_2": text(r, "a:Entity1ToEntity2Role"),
            "role_2_to_1": text(r, "a:Entity2ToEntity1Role"),
        }
        relationships.append(rel)
        for side in (e1, e2):
            if side in entities:
                entities[side]["relationships"].append(rid)

    if by_type.get("o:Inheritance"):
        warn(f"{len(by_type['o:Inheritance'])} herança(s) no modelo não foram detalhadas")

    # Diagramas
    diagrams: dict[str, dict] = {}
    for oid, (t, d, pkg) in objs.items():
        if not t.endswith("Diagram") or t == "o:Diagram":
            continue
        dcode = text(d, "a:Code") or text(d, "a:Name") or oid
        ents: list[str] = []
        for sym in d.iter():
            if tag(sym) != "o:EntitySymbol":
                continue
            for r in refs(sym, "c:Object"):
                eid = resolve_entity(r)
                if eid and eid not in ents:
                    ents.append(eid)
        diagrams[oid] = {
            "id": oid,
            "name": text(d, "a:Name"),
            "code": dcode,
            "comment": text(d, "a:Comment"),
            "package": "/".join(p for p in pkg if p),
            "entities": ents,
        }
        for eid in ents:
            if eid in entities:
                entities[eid]["diagrams"].append(oid)

    return {
        "model": model,
        "last_modification": to_iso(str(last_mod)) if last_mod else "",
        "entities": entities,
        "relationships": {r["id"]: r for r in relationships},
        "diagrams": diagrams,
    }


# ------------------------------------------------------- chaves de arquivo
SAFE_RE = re.compile(r"[^A-Za-z0-9_.-]+")


def assign_keys(items: dict[str, dict], kind: str) -> dict[str, str]:
    """Id -> chave única e segura para nome de arquivo (code; colisão => prefixa pacote)."""
    keys: dict[str, str] = {}
    seen: dict[str, str] = {}
    for oid in sorted(items, key=lambda i: (items[i]["code"], items[i]["package"], i)):
        it = items[oid]
        base = SAFE_RE.sub("_", it["code"]).strip("_") or oid
        key = base
        if key.lower() in seen:
            pref = SAFE_RE.sub("_", it["package"]).strip("_")
            key = f"{pref}__{base}" if pref else f"{base}__{oid}"
            warn(f"{kind} com código repetido: {it['code']} (salvo como {key})")
        seen[key.lower()] = oid
        keys[oid] = key
    return keys


# ------------------------------------------------------------- catalog.json
def build_catalog(m: dict, src: Path, sha: str) -> dict:
    ekeys = assign_keys(m["entities"], "Tabela")
    dkeys = assign_keys(m["diagrams"], "Diagrama")

    def ent_label(eid: str) -> str:
        return ekeys[eid] if eid in ekeys else eid.replace("EXT:", "") + " (externo)"

    tables = {}
    for eid, e in m["entities"].items():
        rels = []
        for rid in e["relationships"]:
            r = m["relationships"][rid]
            if r["entity1"] == eid:
                other, mine, theirs = r["entity2"], r["card_2_to_1"], r["card_1_to_2"]
            else:
                other, mine, theirs = r["entity1"], r["card_1_to_2"], r["card_2_to_1"]
            rels.append({
                "name": r["name"], "code": r["code"],
                "with": ent_label(other),
                "cardinality_here": mine, "cardinality_other": theirs,
            })
        tables[ekeys[eid]] = {
            "name": e["name"],
            "code": e["code"],
            "package": e["package"],
            "comment": e["comment"],
            "diagrams": sorted(dkeys[d] for d in e["diagrams"]),
            "primary_key": e["primary_key"],
            "columns": {c: e["columns"][c] for c in e["column_order"]},
            "identifiers": [
                {k: v for k, v in i.items() if k != "id"} for i in e["identifiers"]
            ],
            "relationships": sorted(rels, key=lambda r: (r["with"], r["code"])),
        }
    diagrams = {}
    for did, d in m["diagrams"].items():
        diagrams[dkeys[did]] = {
            "name": d["name"], "code": d["code"], "package": d["package"],
            "comment": d["comment"],
            "tables": sorted(ent_label(e) for e in d["entities"]),
        }
    return {
        "meta": {
            "generator": GENERATOR,
            "source_file": src.name,
            "source_sha256": sha,
            "model_name": m["model"]["name"],
            "model_code": m["model"]["code"],
            "model_last_modification": m["last_modification"],
            "parsed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "counts": {"tables": len(tables), "diagrams": len(diagrams),
                       "relationships": len(m["relationships"])},
        },
        "diagrams": dict(sorted(diagrams.items())),
        "tables": dict(sorted(tables.items())),
    }


# ------------------------------------------------------------------- diff
TRACKED = ("datatype", "length", "precision", "mandatory", "pk")


def _num(v: str) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def diff_catalogs(old: dict | None, new: dict) -> tuple[list[str], list[str]]:
    """Retorna (quebras, demais mudanças)."""
    if not old:
        return [], ["Primeira geração — sem versão anterior para comparar."]
    breaking, other = [], []
    ot, nt = old.get("tables", {}), new["tables"]
    for t in sorted(set(nt) - set(ot)):
        other.append(f"nova tabela `{t}`")
    for t in sorted(set(ot) - set(nt)):
        breaking.append(f"tabela removida `{t}`")
    for t in sorted(set(ot) & set(nt)):
        oc, nc = ot[t]["columns"], nt[t]["columns"]
        for c in sorted(set(nc) - set(oc)):
            msg = f"nova coluna `{t}.{c}`"
            (breaking if nc[c].get("mandatory") else other).append(
                msg + (" (obrigatória)" if nc[c].get("mandatory") else ""))
        for c in sorted(set(oc) - set(nc)):
            breaking.append(f"coluna removida `{t}.{c}`")
        for c in sorted(set(oc) & set(nc)):
            for f in TRACKED:
                a, b = oc[c].get(f), nc[c].get(f)
                if a == b:
                    continue
                msg = f"`{t}.{c}` {f}: {a!r} → {b!r}"
                is_break = (
                    f == "datatype"
                    or (f in ("length", "precision") and _num(b) is not None
                        and _num(a) is not None and _num(b) < _num(a))
                    or (f == "mandatory" and b is True)
                    or f == "pk"
                )
                (breaking if is_break else other).append(msg)
        if ot[t].get("diagrams") != nt[t].get("diagrams"):
            other.append(f"`{t}` diagramas: {ot[t].get('diagrams')} → {nt[t].get('diagrams')}")
    od, nd = old.get("diagrams", {}), new["diagrams"]
    for d in sorted(set(nd) - set(od)):
        other.append(f"novo diagrama `{d}`")
    for d in sorted(set(od) - set(nd)):
        other.append(f"diagrama removido `{d}`")
    return breaking, other


# --------------------------------------------------------------- markdown
def esc(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def first_line(s: str, limit: int = 120) -> str:
    line = next((l.strip() for l in (s or "").splitlines() if l.strip()), "")
    return line if len(line) <= limit else line[: limit - 1] + "…"


def type_str(c: dict) -> str:
    return c["datatype"] or "?"


HEADER = "> Gerado automaticamente pela skill `ldm-sync` a partir de `{src}` — não edite à mão.\n"


def render_table(key: str, t: dict, src: str) -> str:
    out = [f"# {key} — {t['name']}", "", HEADER.format(src=src)]
    if t["diagrams"]:
        out.append("**Diagramas:** " + ", ".join(f"[{d}](../diagrams/{d}.md)" for d in t["diagrams"]))
    else:
        out.append("**Diagramas:** (nenhum)")
    if t["package"]:
        out.append(f"**Pacote:** {t['package']}")
    if t["primary_key"]:
        out.append("**PK:** " + ", ".join(f"`{c}`" for c in t["primary_key"]))
    out.append("")
    if t["comment"]:
        out += [t["comment"], ""]

    out += ["## Colunas", "",
            "| Código | Nome | Tipo | Tam. | Prec. | Obrig. | Chave |",
            "|---|---|---|---|---|---|---|"]
    for code, c in t["columns"].items():
        keys = (["PK"] if c["pk"] else []) + [f"FK→{f}" for f in c["fk"]]
        if c["migrated"] and not c["fk"]:
            keys.append("FK (migrada)")
        out.append(
            f"| `{code}` | {esc(c['name'])} | {esc(type_str(c))} | {c['length']} | "
            f"{c['precision']} | {'sim' if c['mandatory'] else 'não'} | {', '.join(keys)} |"
        )
    out.append("")

    detailed = [(k, c) for k, c in t["columns"].items() if c["comment"] or c["extended"] or c["domain"]]
    if detailed:
        out += ["## Detalhes das colunas", ""]
        for code, c in detailed:
            out += [f"### `{code}`", ""]
            if c["domain"]:
                out.append(f"- **Domínio:** {c['domain']}")
            for k, v in sorted(c["extended"].items()):
                out.append(f"- **{k}:** {v}")
            if c["comment"]:
                out += ["", c["comment"]]
            out.append("")

    if t["relationships"]:
        out += ["## Relacionamentos", "",
                "| Com | Card. aqui | Card. lá | Relacionamento |", "|---|---|---|---|"]
        for r in t["relationships"]:
            w = r["with"]
            link = f"[{w}]({w}.md)" if "(externo)" not in w else w
            out.append(f"| {link} | {r['cardinality_here']} | {r['cardinality_other']} | "
                       f"{esc(r['name'] or r['code'])} |")
        out.append("")

    alt = [i for i in t["identifiers"] if not i["primary"]]
    if alt:
        out += ["## Identificadores alternativos", ""]
        for i in alt:
            out.append(f"- **{i['name'] or i['code']}:** " + ", ".join(f"`{c}`" for c in i["columns"]))
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_diagram(key: str, d: dict, tables: dict, src: str) -> str:
    out = [f"# Diagrama {key} — {d['name']}", "", HEADER.format(src=src)]
    if d["package"]:
        out.append(f"**Pacote:** {d['package']}\n")
    if d["comment"]:
        out += [d["comment"], ""]
    out += [f"## Tabelas ({len(d['tables'])})", "", "| Tabela | Nome | Descrição |", "|---|---|---|"]
    for t in d["tables"]:
        if t in tables:
            out.append(f"| [{t}](../tables/{t}.md) | {esc(tables[t]['name'])} | "
                       f"{esc(first_line(tables[t]['comment']))} |")
        else:
            out.append(f"| {t} | | |")
    out.append("")
    in_diag = set(d["tables"])
    rels = sorted({
        (t, r["with"], r["cardinality_here"], r["cardinality_other"], r["name"] or r["code"])
        for t in d["tables"] if t in tables
        for r in tables[t]["relationships"]
        if r["with"] in in_diag and t < r["with"]
    })
    if rels:
        out += ["## Relacionamentos entre as tabelas do diagrama", ""]
        for a, b, ca, cb, n in rels:
            out.append(f"- `{a}` ({ca}) — `{b}` ({cb}): {n}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def render_index(cat: dict) -> str:
    m = cat["meta"]
    out = [f"# Modelo de dados — {m['model_name']}", "",
           HEADER.format(src=m["source_file"]),
           "Comece aqui. Abra só o diagrama/tabela que a tarefa precisa.", "",
           f"## Diagramas ({len(cat['diagrams'])})", ""]
    for k, d in cat["diagrams"].items():
        desc = first_line(d["comment"])
        out.append(f"- [{k}](diagrams/{k}.md) — {d['name']} ({len(d['tables'])} tabelas)"
                   + (f": {desc}" if desc else ""))
    out += ["", f"## Tabelas ({len(cat['tables'])})", "",
            "| Tabela | Nome | Diagramas | Descrição |", "|---|---|---|---|"]
    for k, t in cat["tables"].items():
        out.append(f"| [{k}](tables/{k}.md) | {esc(t['name'])} | {', '.join(t['diagrams']) or '—'} | "
                   f"{esc(first_line(t['comment']))} |")
    return "\n".join(out).rstrip() + "\n"


def render_meta(cat: dict) -> str:
    m = cat["meta"]
    c = m["counts"]
    return "\n".join([
        "# Metadados do modelo de dados", "",
        f"- **Arquivo de origem:** `{m['source_file']}`",
        f"- **SHA-256:** `{m['source_sha256']}`",
        f"- **Modelo:** {m['model_name']} (`{m['model_code']}`)",
        f"- **Última modificação no PowerDesigner:** {m['model_last_modification'] or 'desconhecida'}",
        f"- **Data do parse:** {m['parsed_at']}",
        f"- **Contagens:** {c['tables']} tabelas, {c['diagrams']} diagramas, {c['relationships']} relacionamentos",
        f"- **Gerador:** {m['generator']}", "",
        "Se a data do parse estiver muito antiga, o modelo pode estar desatualizado: "
        "peça ao time uma nova exportação do .ldm e rode a skill `ldm-sync`.", "",
    ])


def render_diff(breaking: list[str], other: list[str], cat: dict) -> str:
    out = ["# Diff do último parse", "",
           f"Gerado em {cat['meta']['parsed_at']} a partir de `{cat['meta']['source_file']}`.", ""]
    out += ["## ⚠️ Mudanças que podem quebrar", ""] + ([f"- {x}" for x in breaking] or ["- nenhuma"])
    out += ["", "## Outras mudanças", ""] + ([f"- {x}" for x in other] or ["- nenhuma"])
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------- main
def write_output(out: Path, cat: dict, breaking: list[str], other: list[str]) -> None:
    src = cat["meta"]["source_file"]
    for sub in ("tables", "diagrams"):
        if (out / sub).exists():
            shutil.rmtree(out / sub)  # regera do zero: tabela removida no .ldm some daqui
        (out / sub).mkdir(parents=True)
    for k, t in cat["tables"].items():
        (out / "tables" / f"{k}.md").write_text(render_table(k, t, src), encoding="utf-8")
    for k, d in cat["diagrams"].items():
        (out / "diagrams" / f"{k}.md").write_text(render_diagram(k, d, cat["tables"], src), encoding="utf-8")
    (out / "index.md").write_text(render_index(cat), encoding="utf-8")
    (out / "_meta.md").write_text(render_meta(cat), encoding="utf-8")
    (out / "_last-diff.md").write_text(render_diff(breaking, other, cat), encoding="utf-8")
    (out / "catalog.json").write_text(
        json.dumps(cat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="PowerDesigner .ldm (XML) -> base de conhecimento markdown")
    ap.add_argument("ldm", type=Path, help="caminho do .ldm salvo em XML")
    ap.add_argument("--out", type=Path, default=Path("docs/data-model"),
                    help="pasta de saída (default: docs/data-model)")
    ap.add_argument("--dry-run", action="store_true", help="só calcula e mostra o diff, não grava")
    ap.add_argument("--force", action="store_true",
                    help="permite gravar numa pasta não vazia que não foi gerada por esta skill")
    args = ap.parse_args()

    if not args.ldm.is_file():
        sys.exit(f"ERRO: arquivo não encontrado: {args.ldm}")

    out: Path = args.out
    if out.exists() and any(out.iterdir()) and not (out / "catalog.json").exists() and not args.force:
        sys.exit(f"ERRO: {out} não está vazia e não tem catalog.json — não parece uma pasta gerada "
                 "por esta skill. Confira o caminho ou use --force.")

    sha = hashlib.sha256(args.ldm.read_bytes()).hexdigest()
    model = parse_model(args.ldm)
    cat = build_catalog(model, args.ldm, sha)

    old = None
    if (out / "catalog.json").exists():
        try:
            old = json.loads((out / "catalog.json").read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            warn("catalog.json anterior ilegível — diff não calculado")
    if old and old.get("meta", {}).get("source_sha256") == sha:
        print("Nada mudou: o .ldm é idêntico ao do último parse.")
        return 0

    breaking, other = diff_catalogs(old, cat)

    c = cat["meta"]["counts"]
    print(f"Modelo: {cat['meta']['model_name']} — {c['tables']} tabelas, "
          f"{c['diagrams']} diagramas, {c['relationships']} relacionamentos")
    print(f"\nMudanças que podem quebrar: {len(breaking)}")
    for x in breaking:
        print("  " + x)
    print(f"Outras mudanças: {len(other)}")
    for x in other[:50]:
        print("  " + x)
    if len(other) > 50:
        print(f"  … (+{len(other) - 50}, veja _last-diff.md)")

    orphan = [k for k, t in cat["tables"].items() if not t["diagrams"]]
    if orphan:
        warn(f"{len(orphan)} tabela(s) fora de qualquer diagrama: {', '.join(orphan[:10])}"
             + ("…" if len(orphan) > 10 else ""))
    if WARNINGS:
        print(f"\nAvisos ({len(WARNINGS)}):")
        for w in WARNINGS[:30]:
            print("  - " + w)
        if len(WARNINGS) > 30:
            print(f"  … (+{len(WARNINGS) - 30})")

    if args.dry_run:
        print("\n--dry-run: nada foi gravado.")
        return 0

    out.mkdir(parents=True, exist_ok=True)
    write_output(out, cat, breaking, other)
    print(f"\nGravado em {out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
