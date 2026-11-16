"""rodar_sensores.py (hook Stop/SubagentStop)."""
import json
import sys

from conftest import ativar


def configurar(repo, codigo_saida, quando=("*.java",)):
    pasta = repo / ".harness"
    pasta.mkdir(exist_ok=True)
    cmd = f'"{sys.executable}" -c "print(\'saida do sensor\'); raise SystemExit({codigo_saida})"'
    (pasta / "sensores.json").write_text(json.dumps(
        {"sensores": [{"nome": "build", "quando": list(quando), "comando": cmd}]}), encoding="utf-8")


def resultado(runs):
    return json.loads((runs / "PROJ-1" / "sensores.json").read_text(encoding="utf-8"))


def test_sem_execucao_ativa_nao_faz_nada(rodar, home):
    assert rodar("sensores").returncode == 0


def test_sensor_so_roda_se_arquivo_casar(rodar, runs, repo_git):
    app = repo_git("app")
    configurar(app, 1)
    ativar(runs, "PROJ-1", [app])
    (app / "notas.txt").write_text("x", encoding="utf-8")  # não casa com *.java
    assert rodar("sensores").returncode == 0
    assert resultado(runs) == []


def test_sensor_ok(rodar, runs, repo_git):
    app = repo_git("app")
    configurar(app, 0)
    ativar(runs, "PROJ-1", [app])
    (app / "X.java").write_text("class X {}", encoding="utf-8")
    assert rodar("sensores").returncode == 0
    assert resultado(runs) == [{"repo": "app", "sensor": "build", "ok": True}]


def test_sensor_casa_arquivo_em_subpasta(rodar, runs, repo_git):
    app = repo_git("app")
    configurar(app, 1)
    ativar(runs, "PROJ-1", [app])
    (app / "src" / "main").mkdir(parents=True)
    (app / "src" / "main" / "X.java").write_text("class X {}", encoding="utf-8")
    assert rodar("sensores").returncode == 2


def test_falha_devolve_erro_e_escala_depois_de_3(rodar, runs, repo_git):
    app = repo_git("app")
    configurar(app, 1)
    ativar(runs, "PROJ-1", [app])
    (app / "X.java").write_text("class X {}", encoding="utf-8")

    for tentativa in (1, 2, 3):
        r = rodar("sensores")
        assert r.returncode == 2
        assert f"tentativa {tentativa}/3" in r.stderr and "saida do sensor" in r.stderr
    r = rodar("sensores")
    assert r.returncode == 0 and "Pare e reporte" in r.stderr  # 4ª: libera e escala

    log = (runs / "PROJ-1" / "log.jsonl").read_text(encoding="utf-8")
    assert '"valor": "falha build"' in log


def test_sucesso_zera_tentativas(rodar, runs, repo_git):
    app = repo_git("app")
    configurar(app, 1)
    ativar(runs, "PROJ-1", [app])
    (app / "X.java").write_text("class X {}", encoding="utf-8")
    rodar("sensores")
    configurar(app, 0)
    assert rodar("sensores").returncode == 0
    assert not (runs / "PROJ-1" / "tentativas_sensores").exists()
