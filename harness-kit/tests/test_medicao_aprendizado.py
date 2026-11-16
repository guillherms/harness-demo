"""registrar.py, relatorio.py e aprendizado.py."""
import json

from conftest import ativar


def eventos(runs, historia):
    return [json.loads(l) for l in (runs / historia / "log.jsonl").read_text(encoding="utf-8").splitlines()]


def test_registrar_sem_execucao_ativa_nao_grava(rodar, runs):
    assert rodar("registrar", "marcar", "review", "APROVADO").returncode == 0
    assert list(runs.iterdir()) == []


def test_registrar_marco_e_hook(rodar, runs, tmp_path):
    ativar(runs, "PROJ-1", [tmp_path])
    rodar("registrar", "marcar", "review", "REPROVADO")
    rodar("registrar", stdin={"hook_event_name": "PostToolUse", "session_id": "s1",
                              "tool_name": "Read", "tool_input": {"file_path": "C:/x/A.java"}})
    e = eventos(runs, "PROJ-1")
    assert e[0]["evento"] == "marco" and e[0]["valor"] == "REPROVADO"
    assert e[1]["ferramenta"] == "Read" and e[1]["alvo"] == "C:/x/A.java"


def test_registrar_nunca_quebra(rodar, runs, tmp_path):
    ativar(runs, "PROJ-1", [tmp_path])
    assert rodar("registrar", stdin="isto não é json").returncode == 0


def test_relatorio(rodar, runs, tmp_path):
    ativar(runs, "PROJ-1", [tmp_path])
    for ev in ({"hook_event_name": "UserPromptSubmit"},
               {"hook_event_name": "PostToolUse", "tool_name": "Read", "tool_input": {"file_path": "a"}},
               {"hook_event_name": "PostToolUse", "tool_name": "Edit", "tool_input": {"file_path": "a"}},
               {"hook_event_name": "SubagentStop"}):
        rodar("registrar", stdin=ev)
    rodar("registrar", "marcar", "review", "REPROVADO")
    rodar("registrar", "marcar", "review", "APROVADO")
    r = rodar("relatorio", "PROJ-1", "--json")
    assert r.returncode == 0, r.stderr
    resumo = json.loads(r.stdout)
    assert resumo["leituras"] == 1 and resumo["edicoes"] == 1
    assert resumo["rodadas_review"] == 2 and resumo["reprovacoes_review"] == 1
    assert resumo["subagents_concluidos"] == 1
    assert (runs / "PROJ-1" / "resumo.json").exists()


def test_aprendizado_agrupa_e_respeita_corte(rodar, runs, tmp_path):
    for h in ("H-1", "H-2"):
        ativar(runs, h, [tmp_path])
        rodar("registrar", "marcar", "apontamento", "testes", "[B1] A.java:1: erro sem teste")
    rodar("registrar", "marcar", "apontamento", "nomes", "[S1] uma vez só")

    r = rodar("aprendizado", "analisar")
    assert "testes: 2x em 2 história(s)" in r.stdout
    assert "nomes" not in r.stdout  # só 1 ocorrência

    rodar("aprendizado", "aplicar", "--categoria", "testes", "--onde", "AGENTS.md", "--descricao", "regra")
    assert "Nada recorrente" in rodar("aprendizado", "analisar").stdout
