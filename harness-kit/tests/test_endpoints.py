"""Lógica do MCP local (endpoints.py), sem depender do pacote mcp."""
import importlib.util
import json

import pytest

from conftest import SCRIPTS

CONTROLLER_PADRAO = """package app.entrypoint;

@RestController
@RequestMapping("/contratos")
public class ContratoController {
    @GetMapping("/{id}")
    public Contrato buscar(String id) { return null; }

    @PostMapping
    public Contrato criar(Contrato c) { return null; }
}
"""

CONTROLLER_LEGADO = """package app.legado;

@Controller
public class ClienteAntigoController {
    @RequestMapping(value = "/clientes", method = RequestMethod.GET)
    public String listar() { return null; }
}
"""


@pytest.fixture
def ep():
    spec = importlib.util.spec_from_file_location("endpoints", SCRIPTS["endpoints"])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def repo(tmp_path):
    fonte = tmp_path / "src" / "main" / "java" / "app"
    (fonte / "entrypoint").mkdir(parents=True)
    (fonte / "legado").mkdir()
    (fonte / "entrypoint" / "ContratoController.java").write_text(CONTROLLER_PADRAO, encoding="utf-8")
    (fonte / "legado" / "ClienteAntigoController.java").write_text(CONTROLLER_LEGADO, encoding="utf-8")
    (fonte / "Util.java").write_text("class Util {}", encoding="utf-8")
    return tmp_path


def test_listar(ep, repo):
    rotas = {(e["metodo"], e["path"], e["padrao"]) for e in ep.listar(str(repo))}
    assert rotas == {
        ("GET", "/contratos/{id}", "padrao"),
        ("POST", "/contratos", "padrao"),
        ("GET", "/clientes", "legado"),
    }


def test_marcador_padrao_configuravel(ep, repo):
    (repo / ".harness").mkdir()
    (repo / ".harness" / "mcp.json").write_text(json.dumps({"marcador_padrao": "legado"}), encoding="utf-8")
    padrao = {e["path"] for e in ep.listar(str(repo)) if e["padrao"] == "padrao"}
    assert padrao == {"/clientes"}


def test_comparar_com_contrato(ep, repo):
    contrato = repo / "openapi.json"
    contrato.write_text(json.dumps({"paths": {
        "/contratos/{contratoId}": {"get": {}},     # nome do param diferente: mesmo endpoint
        "/contratos/{id}/parcelas": {"get": {}},    # só no contrato
    }}), encoding="utf-8")
    r = ep.comparar(str(contrato), str(repo))
    assert r["em_ambos"] == 1
    assert r["so_no_contrato"] == ["GET /contratos/{id}/parcelas"]
    assert r["so_no_codigo"] == ["GET /clientes", "POST /contratos"]


def test_comparar_yaml_com_prefixo(ep, repo):
    pytest.importorskip("yaml")
    contrato = repo / "openapi.yaml"
    contrato.write_text("paths:\n  /v1/contratos:\n    post: {}\n", encoding="utf-8")
    r = ep.comparar(str(contrato), str(repo), prefixo_contrato="/v1")
    assert r["em_ambos"] == 1


def test_cli_listar(rodar, repo):
    r = rodar("endpoints", "listar", repo)
    assert r.returncode == 0 and "/contratos/{id}" in r.stdout
