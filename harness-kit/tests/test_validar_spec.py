import copy
import json

import pytest

pytest.importorskip("jsonschema")

SPEC = {
    "historia": "PROJ-1",
    "pendencias": [],
    "endpoints": [{
        "operacao": "criar",
        "metodo": "GET",
        "path": "/contratos/{id}/parcelas",
        "descricao": "Lista as parcelas de um contrato",
        "request": {"path_params": [{"nome": "id", "tipo": "string", "obrigatorio": True}]},
        "response": {"status": 200, "body": [{"nome": "valor", "tipo": "number", "obrigatorio": True}]},
        "erros": [{"status": 404, "quando": "contrato não existe"}],
    }],
}


def gravar(pasta, spec):
    arq = pasta / "spec.json"
    arq.write_text(json.dumps(spec), encoding="utf-8")
    return arq


def spec_com(**mudancas):
    s = copy.deepcopy(SPEC)
    ep = s["endpoints"][0]
    for chave, valor in mudancas.items():
        if chave in s:
            s[chave] = valor
        else:
            ep[chave] = valor
    return s


def test_spec_valida(tmp_path, rodar, home):
    r = rodar("validar_spec", gravar(tmp_path, SPEC), "--pronta")
    assert r.returncode == 0, r.stderr
    assert "Spec válida" in r.stdout


@pytest.mark.parametrize("spec, trecho", [
    (spec_com(metodo="FETCH"), "metodo"),
    (spec_com(path="sem-barra"), "path"),
    (spec_com(request={}), "path_params"),                                   # {id} sem declarar
    (spec_com(request={"path_params": [{"nome": "id", "tipo": "string", "obrigatorio": True}],
                       "body": [{"nome": "x", "tipo": "string", "obrigatorio": True}]}), "não deve ter body"),
])
def test_spec_invalida(tmp_path, rodar, home, spec, trecho):
    r = rodar("validar_spec", gravar(tmp_path, spec))
    assert r.returncode == 1
    assert trecho in r.stderr


def test_endpoint_duplicado(tmp_path, rodar, home):
    s = copy.deepcopy(SPEC)
    s["endpoints"].append(copy.deepcopy(s["endpoints"][0]))
    r = rodar("validar_spec", gravar(tmp_path, s))
    assert r.returncode == 1 and "duplicado" in r.stderr


def test_pronta_exige_zero_pendencias(tmp_path, rodar, home):
    arq = gravar(tmp_path, spec_com(pendencias=["faltando: status de erro"]))
    assert rodar("validar_spec", arq).returncode == 0           # sem --pronta, passa
    r = rodar("validar_spec", arq, "--pronta")
    assert r.returncode == 1 and "pendência" in r.stderr


def test_hook_ignora_arquivo_fora_de_runs(tmp_path, rodar, home):
    outro = tmp_path / "Qualquer.java"
    outro.write_text("class X {}", encoding="utf-8")
    r = rodar("validar_spec", stdin={"tool_input": {"file_path": str(outro)}})
    assert r.returncode == 0


def test_hook_bloqueia_spec_invalida_em_runs(rodar, runs):
    pasta = runs / "PROJ-1"
    pasta.mkdir()
    arq = gravar(pasta, spec_com(metodo="FETCH"))
    r = rodar("validar_spec", stdin={"tool_input": {"file_path": str(arq)}})
    assert r.returncode == 2 and "Spec inválida" in r.stderr


def test_hook_aceita_spec_valida_em_runs(rodar, runs):
    pasta = runs / "PROJ-1"
    pasta.mkdir()
    r = rodar("validar_spec", stdin={"tool_input": {"file_path": str(gravar(pasta, SPEC))}})
    assert r.returncode == 0, r.stderr
