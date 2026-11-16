"""Cria um ambiente local para testar o harness no Claude Code sem tocar nos repos reais.

    python tests/sandbox/criar_sandbox.py --destino C:/dev/harness-sandbox
    python tests/sandbox/criar_sandbox.py --destino C:/dev/harness-sandbox --limpar

Cria em <destino>:
    remotes/aplicacao-java.git, remotes/gateway-padrao.git   (remotes bare locais)
    aplicacao-java/   Java mínimo que compila com javac puro (sem Maven/Spring)
    gateway-padrao/   contrato openapi.yaml
    historias/        textos de história para colar no Claude Code

Os dois repos recebem o kit via sync.py, já com AGENTS.md, project.yaml e
sensores preenchidos para o sandbox. Também cria ~/.harness/workspace.yaml se
ele ainda não existir.
"""
import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[2]
HARNESS = Path.home() / ".harness"
WORKSPACE = HARNESS / "workspace.yaml"
MARCA = "# criado pelo sandbox do harness-kit"

# ---------------------------------------------------------------- aplicação

ANOTACOES = {
    "RestController": "@Retention(RetentionPolicy.RUNTIME) @Target(ElementType.TYPE)\npublic @interface RestController {}",
    "RequestMapping": "@Retention(RetentionPolicy.RUNTIME)\npublic @interface RequestMapping {\n    String value() default \"\";\n    RequestMethod[] method() default {};\n}",
    "GetMapping": "@Retention(RetentionPolicy.RUNTIME) @Target(ElementType.METHOD)\npublic @interface GetMapping { String value() default \"\"; }",
    "PostMapping": "@Retention(RetentionPolicy.RUNTIME) @Target(ElementType.METHOD)\npublic @interface PostMapping { String value() default \"\"; }",
    "PutMapping": "@Retention(RetentionPolicy.RUNTIME) @Target(ElementType.METHOD)\npublic @interface PutMapping { String value() default \"\"; }",
    "DeleteMapping": "@Retention(RetentionPolicy.RUNTIME) @Target(ElementType.METHOD)\npublic @interface DeleteMapping { String value() default \"\"; }",
    "PathVariable": "@Retention(RetentionPolicy.RUNTIME) @Target(ElementType.PARAMETER)\npublic @interface PathVariable {}",
    "RequestParam": "@Retention(RetentionPolicy.RUNTIME) @Target(ElementType.PARAMETER)\npublic @interface RequestParam { String value() default \"\"; }",
    "RequestBody": "@Retention(RetentionPolicy.RUNTIME) @Target(ElementType.PARAMETER)\npublic @interface RequestBody {}",
}

ARQUIVOS_APP = {
    "src/main/java/sandbox/web/RequestMethod.java":
        "package sandbox.web;\n\npublic enum RequestMethod { GET, POST, PUT, PATCH, DELETE }\n",
    "src/main/java/sandbox/web/NaoEncontradoException.java": """package sandbox.web;

/** Vira HTTP 404. */
public class NaoEncontradoException extends RuntimeException {
    public NaoEncontradoException(String mensagem) { super(mensagem); }
}
""",
    "src/main/java/sandbox/web/Pagina.java": """package sandbox.web;

import java.util.List;

/** Envelope padrão de resposta paginada. */
public record Pagina<T>(List<T> itens, int pagina, int tamanho, long total) {
    public static final int TAMANHO_PADRAO = 20;
    public static final int TAMANHO_MAXIMO = 100;
}
""",
    "src/main/java/sandbox/domain/Contrato.java": """package sandbox.domain;

import java.math.BigDecimal;

public record Contrato(String id, String clienteId, BigDecimal valorTotal, int quantidadeParcelas) {}
""",
    "src/main/java/sandbox/domain/ContratoRepository.java": """package sandbox.domain;

import java.util.List;
import java.util.Optional;

public interface ContratoRepository {
    Optional<Contrato> buscarPorId(String id);
    List<Contrato> listar(int pagina, int tamanho);
    long contar();
}
""",
    "src/main/java/sandbox/application/BuscarContratoUseCase.java": """package sandbox.application;

import sandbox.domain.Contrato;
import sandbox.domain.ContratoRepository;
import sandbox.web.NaoEncontradoException;

public class BuscarContratoUseCase {
    private final ContratoRepository repository;

    public BuscarContratoUseCase(ContratoRepository repository) { this.repository = repository; }

    public Contrato executar(String id) {
        return repository.buscarPorId(id)
                .orElseThrow(() -> new NaoEncontradoException("Contrato " + id + " não encontrado"));
    }
}
""",
    "src/main/java/sandbox/application/ListarContratosUseCase.java": """package sandbox.application;

import sandbox.domain.Contrato;
import sandbox.domain.ContratoRepository;
import sandbox.web.Pagina;

public class ListarContratosUseCase {
    private final ContratoRepository repository;

    public ListarContratosUseCase(ContratoRepository repository) { this.repository = repository; }

    public Pagina<Contrato> executar(int pagina, int tamanho) {
        int t = Math.min(tamanho <= 0 ? Pagina.TAMANHO_PADRAO : tamanho, Pagina.TAMANHO_MAXIMO);
        return new Pagina<>(repository.listar(pagina, t), pagina, t, repository.contar());
    }
}
""",
    "src/main/java/sandbox/entrypoint/ContratoController.java": """package sandbox.entrypoint;

import sandbox.application.BuscarContratoUseCase;
import sandbox.application.ListarContratosUseCase;
import sandbox.domain.Contrato;
import sandbox.web.*;

/** Endpoint de referência: simples (buscar) e paginado (listar). */
@RestController
@RequestMapping("/contratos")
public class ContratoController {
    private final BuscarContratoUseCase buscar;
    private final ListarContratosUseCase listar;

    public ContratoController(BuscarContratoUseCase buscar, ListarContratosUseCase listar) {
        this.buscar = buscar;
        this.listar = listar;
    }

    @GetMapping("/{id}")
    public ContratoResponse buscar(@PathVariable String id) {
        return ContratoResponse.de(buscar.executar(id));
    }

    @GetMapping
    public Pagina<ContratoResponse> listar(@RequestParam("pagina") int pagina,
                                           @RequestParam("tamanho") int tamanho) {
        Pagina<Contrato> p = listar.executar(pagina, tamanho);
        return new Pagina<>(p.itens().stream().map(ContratoResponse::de).toList(),
                p.pagina(), p.tamanho(), p.total());
    }
}
""",
    "src/main/java/sandbox/entrypoint/ContratoResponse.java": """package sandbox.entrypoint;

import java.math.BigDecimal;
import sandbox.domain.Contrato;

public record ContratoResponse(String id, String clienteId, BigDecimal valorTotal, int quantidadeParcelas) {
    public static ContratoResponse de(Contrato c) {
        return new ContratoResponse(c.id(), c.clienteId(), c.valorTotal(), c.quantidadeParcelas());
    }
}
""",
    "src/main/java/sandbox/legado/ClienteAntigoController.java": """package sandbox.legado;

import sandbox.web.*;

/** LEGADO: anterior ao padrão atual. Acessa dados direto, sem use case. Não copie. */
@RestController
public class ClienteAntigoController {
    @RequestMapping(value = "/clientes", method = RequestMethod.GET)
    public String listarClientes() {
        return "[]";
    }
}
""",
    "src/test/java/sandbox/application/BuscarContratoUseCaseTest.java": """package sandbox.application;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import sandbox.domain.Contrato;
import sandbox.domain.ContratoRepository;
import sandbox.web.NaoEncontradoException;

/** Padrão de teste do sandbox: classe *Test com main; cada cenário é um método. */
public class BuscarContratoUseCaseTest {
    static final Contrato CONTRATO = new Contrato("c1", "cli1", new BigDecimal("1200.00"), 12);

    static ContratoRepository repoCom(Contrato... contratos) {
        return new ContratoRepository() {
            public Optional<Contrato> buscarPorId(String id) {
                return List.of(contratos).stream().filter(c -> c.id().equals(id)).findFirst();
            }
            public List<Contrato> listar(int pagina, int tamanho) { return List.of(contratos); }
            public long contar() { return contratos.length; }
        };
    }

    static void deveRetornarContratoExistente() {
        Contrato c = new BuscarContratoUseCase(repoCom(CONTRATO)).executar("c1");
        Assert.igual("c1", c.id());
    }

    static void deveLancarNaoEncontradoQuandoNaoExiste() {
        Assert.lanca(NaoEncontradoException.class, () -> new BuscarContratoUseCase(repoCom()).executar("x"));
    }

    public static void main(String[] args) {
        deveRetornarContratoExistente();
        deveLancarNaoEncontradoQuandoNaoExiste();
    }
}
""",
    "src/test/java/sandbox/application/Assert.java": """package sandbox.application;

/** Asserções mínimas (o sandbox não tem JUnit). */
public final class Assert {
    private Assert() {}

    public static void igual(Object esperado, Object atual) {
        if (esperado == null ? atual != null : !esperado.equals(atual)) {
            throw new AssertionError("esperado <" + esperado + "> mas foi <" + atual + ">");
        }
    }

    public static void lanca(Class<? extends Throwable> tipo, Runnable acao) {
        try {
            acao.run();
        } catch (Throwable t) {
            if (tipo.isInstance(t)) return;
            throw new AssertionError("esperado " + tipo.getSimpleName() + " mas foi " + t);
        }
        throw new AssertionError("esperado " + tipo.getSimpleName() + ", nada foi lançado");
    }
}
""",
    ".harness/compilar.py": r'''"""Build + testes do sandbox (substitui o `mvn -q verify`).

Compila src/main e src/test com javac e roda o main() de cada classe *Test.
"""
import shutil
import subprocess
import sys
from pathlib import Path

raiz = Path(__file__).resolve().parent.parent
alvo = raiz / "target"
shutil.rmtree(alvo, ignore_errors=True)
fontes = [str(p) for p in (raiz / "src").rglob("*.java")]
r = subprocess.run(["javac", "-encoding", "UTF-8", "-d", str(alvo), *fontes])
if r.returncode != 0:
    sys.exit("BUILD FALHOU")
falhas = 0
for teste in sorted((raiz / "src" / "test" / "java").rglob("*Test.java")):
    classe = ".".join(teste.relative_to(raiz / "src" / "test" / "java").with_suffix("").parts)
    r = subprocess.run(["java", "-ea", "-cp", str(alvo), classe])
    print(f"{'OK   ' if r.returncode == 0 else 'FALHA'} {classe}")
    falhas += r.returncode != 0
sys.exit(f"{falhas} classe(s) de teste falharam" if falhas else 0)
''',
    ".gitignore": "target/\n",
}

AGENTS_APP = """# Aplicação Java (sandbox do harness)

## Visão geral
Aplicação de contratos de crédito. Expõe endpoints REST consumidos pelo BFF.
**É um sandbox**: Java puro, sem Spring nem Maven; as anotações de `sandbox.web`
imitam as do Spring.

## Comandos
- Build + testes: `python .harness/compilar.py`
- TAAC: não existe no sandbox.
- Rode o build + testes antes de considerar uma tarefa pronta.

## Arquitetura
- Camadas: `entrypoint` → `application` → `domain`. `domain` não depende de nada.
- Controller nunca acessa repository: sempre via use case em `application/`.
- Um use case por operação (`<Verbo><Entidade>UseCase`, método `executar`).
- Resposta do controller é um `*Response` (record) em `entrypoint/`, nunca a entidade.
- Recurso inexistente: lance `NaoEncontradoException` (vira 404).
Detalhes: `docs/arquitetura.md`

## Mapa do projeto
- `src/main/java/sandbox/entrypoint`: controllers e responses
- `src/main/java/sandbox/application`: use cases
- `src/main/java/sandbox/domain`: entidades e interfaces de repository
- `src/main/java/sandbox/web`: anotações e tipos de infraestrutura web
- `src/test/java`: testes
- Contrato OpenAPI: no repo `gateway-padrao` (veja `.harness/project.yaml`).

## Referências e legado
- Endpoints de referência (use estes como exemplo, não outros):
  - simples: `ContratoController#buscar` (`GET /contratos/{id}`)
  - paginado: `ContratoController#listar` (`GET /contratos`)
- Legado (não use como exemplo): tudo em `sandbox/legado/`.
- Não refatore código fora do escopo da tarefa sem pedido explícito.

## Padrões (leia só quando a tarefa pedir)
- Criar/alterar endpoint: `docs/patterns/endpoint.md`
- Paginação: `docs/patterns/paginacao.md`
- Testes: `docs/patterns/testes.md`

## Harness
- Este repo tem par: veja `.harness/project.yaml`.
- Histórias são desenvolvidas pela skill `desenvolver-historia`.
"""

DOCS_APP = {
    "docs/arquitetura.md": "# Arquitetura\n\nentrypoint → application → domain. `domain` não importa nada de `web`, "
                           "`application` ou `entrypoint`.\n",
    "docs/patterns/endpoint.md": """# Padrão: criar endpoint

1. Use case em `application/` (`<Verbo><Entidade>UseCase`, método `executar`).
2. Se precisar de dado novo, método novo na interface do repository em `domain/`.
3. Método no controller da entidade em `entrypoint/` (crie o controller se não houver).
4. Resposta como record `*Response` em `entrypoint/`, com fábrica estática `de(...)`.
5. Erros de negócio como exceções; inexistente → `NaoEncontradoException` (404).
6. Testes do use case (veja `testes.md`).
""",
    "docs/patterns/paginacao.md": """# Padrão: paginação

- Query params `pagina` (começa em 0) e `tamanho`.
- Tamanho padrão 20, máximo 100 (`Pagina.TAMANHO_PADRAO` / `TAMANHO_MAXIMO`).
- Resposta no envelope `Pagina<T>` (`itens`, `pagina`, `tamanho`, `total`).
- Referência: `ContratoController#listar`.
""",
    "docs/patterns/testes.md": """# Padrão: testes

- Sem JUnit no sandbox: uma classe `<Classe>Test` em `src/test/java`, mesmo pacote,
  com `main` chamando um método estático por cenário (`deve...`).
- Asserções com `sandbox.application.Assert` (`igual`, `lanca`).
- Um cenário por regra de negócio e por erro da spec.
- Repository falso como classe anônima (veja `BuscarContratoUseCaseTest`).
- `python .harness/compilar.py` roda tudo.
""",
}

PROJECT_APP = """repo: aplicacao-java
tipo: aplicacao

par:
  repo: gateway-padrao
  papel: contrato-openapi
  regra: toda criação, alteração ou exclusão de rota reflete no contrato

fase_seguinte:
  descricao: história do BFF (não existe no sandbox)
  repos: []

branch:
  padrao: "feature/{historia}"
  base: develop
"""

SENSORES_APP = {"sensores": [{"nome": "build-e-testes", "quando": ["*.java"],
                              "comando": "python .harness/compilar.py"}]}

# ---------------------------------------------------------------- gateway

CONTRATO = """openapi: 3.0.3
info:
  title: API de contratos
  version: 1.0.0
paths:
  /contratos/{id}:
    get:
      summary: Busca um contrato
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string }
      responses:
        "200":
          description: Contrato encontrado
          content:
            application/json:
              schema: { $ref: "#/components/schemas/Contrato" }
        "404":
          description: Contrato não encontrado
  /contratos:
    get:
      summary: Lista contratos (paginado)
      parameters:
        - { name: pagina, in: query, required: false, schema: { type: integer, default: 0 } }
        - { name: tamanho, in: query, required: false, schema: { type: integer, default: 20, maximum: 100 } }
      responses:
        "200":
          description: Página de contratos
          content:
            application/json:
              schema: { $ref: "#/components/schemas/PaginaContrato" }
  /clientes:
    get:
      summary: Lista clientes (legado)
      responses:
        "200": { description: Clientes }
components:
  schemas:
    Contrato:
      type: object
      required: [id, clienteId, valorTotal, quantidadeParcelas]
      properties:
        id: { type: string }
        clienteId: { type: string }
        valorTotal: { type: number }
        quantidadeParcelas: { type: integer }
    PaginaContrato:
      type: object
      properties:
        itens: { type: array, items: { $ref: "#/components/schemas/Contrato" } }
        pagina: { type: integer }
        tamanho: { type: integer }
        total: { type: integer }
"""

VALIDAR_CONTRATO = r'''"""Sensor do contrato: usa openapi-spec-validator se instalado; senão, checagem mínima."""
import sys
from pathlib import Path

arq = Path(__file__).resolve().parent.parent / "openapi.yaml"
try:
    from openapi_spec_validator import validate
    from openapi_spec_validator.readers import read_from_filename
except ImportError:
    import yaml
    doc = yaml.safe_load(arq.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or "openapi" not in doc or not isinstance(doc.get("paths"), dict):
        sys.exit("contrato inválido: faltam 'openapi' ou 'paths'")
    print("contrato OK (checagem mínima: instale openapi-spec-validator para validar de verdade)")
else:
    try:
        validate(read_from_filename(str(arq))[0])
    except Exception as e:
        sys.exit(f"contrato inválido: {e}")
    print("contrato OK")
'''

AGENTS_GW = """# Gateway (sandbox do harness)

## Visão geral
Contrato OpenAPI exposto pelo API Gateway para `aplicacao-java`.

## Onde fica o contrato
- `openapi.yaml`

## Convenções
- Paths no plural e em minúsculas (`/contratos/{id}/parcelas`).
- Schemas em `components/schemas`, nome em PascalCase igual ao recurso.
- Todo endpoint documenta o 200 e cada erro de negócio (ex.: 404).
- Listas paginadas usam `pagina`/`tamanho` e um schema `Pagina<Recurso>`.
- Exemplo bom para copiar: `GET /contratos` e `GET /contratos/{id}`.

## Validação
- `python .harness/validar_contrato.py`
"""

PROJECT_GW = """repo: gateway-padrao
tipo: gateway
contrato: openapi.yaml

branch:
  padrao: "feature/{historia}"
  base: develop
"""

SENSORES_GW = {"sensores": [{"nome": "openapi-valido", "quando": ["*.yaml", "*.yml"],
                             "comando": "python .harness/validar_contrato.py"}]}

# ---------------------------------------------------------------- histórias

HISTORIAS = {
    "SBX-1-parcelas.md": """SBX-1 — Listar parcelas de um contrato

Como atendente, quero consultar as parcelas de um contrato para informar o cliente.

Endpoint: GET /contratos/{id}/parcelas

Critérios de aceite:
- Retorna a lista de parcelas do contrato, ordenada pelo número da parcela.
- Cada parcela tem: numero (inteiro), vencimento (data), valor (decimal) e
  situacao (texto: ABERTA, PAGA ou ATRASADA).
- Se o contrato não existir, retorna 404.
- Não é paginado: um contrato tem no máximo 120 parcelas.
""",
    "SBX-2-cancelar.md": """SBX-2 — Cancelar contrato

Como gerente, quero cancelar um contrato.

Precisamos de um endpoint para cancelar contratos. Só pode cancelar se o
cliente estiver ok. Contrato já cancelado não pode ser cancelado de novo.
""",
    "SBX-3-tamanho-pagina.md": """SBX-3 — Aumentar o tamanho padrão da página

A listagem de contratos está devolvendo poucos itens por padrão. O tamanho
padrão da página deve passar de 20 para 50. O máximo continua 100.
Nenhuma rota muda.
""",
}

LEIA_ME = """# Histórias do sandbox

Abra o Claude Code em `aplicacao-java/` e cole uma destas, por exemplo:

    /desenvolver-historia SBX-1
    <cole aqui o texto de SBX-1-parcelas.md>

- SBX-1: criar endpoint com tudo que precisa (caminho feliz).
- SBX-2: dados faltando de propósito (método, path, regra vaga "cliente ok",
  status dos erros): deve gerar pendências 🟡/❌ e perguntas em lote.
- SBX-3: não mexe em rota: deve cair no fluxo genérico.

Roteiro completo: `harness-kit/docs/testes.md`.
"""

# ---------------------------------------------------------------- execução


def sh(*args, cwd=None):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ERRO: {' '.join(map(str, args))}\n{r.stdout}{r.stderr}")
    return r.stdout.strip()


def escrever(raiz: Path, arquivos: dict):
    for rel, conteudo in arquivos.items():
        arq = raiz / rel
        arq.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(conteudo, (dict, list)):
            conteudo = json.dumps(conteudo, indent=2, ensure_ascii=False) + "\n"
        arq.write_text(conteudo, encoding="utf-8", newline="\n")


def criar_repo(destino: Path, nome: str) -> Path:
    remoto = destino / "remotes" / f"{nome}.git"
    sh("git", "init", "-q", "--bare", str(remoto))
    repo = destino / nome
    sh("git", "init", "-q", "-b", "develop", str(repo))
    sh("git", "-C", str(repo), "remote", "add", "origin", str(remoto))
    if not subprocess.run(["git", "-C", str(repo), "config", "user.email"], capture_output=True).stdout.strip():
        sh("git", "-C", str(repo), "config", "user.email", "sandbox@harness.local")
        sh("git", "-C", str(repo), "config", "user.name", "Sandbox")
    return repo


def publicar(repo: Path, mensagem: str):
    sh("git", "-C", str(repo), "add", "-A")
    # --no-verify: commit de montagem do sandbox, não é trabalho de uma história
    sh("git", "-C", str(repo), "commit", "-q", "--no-verify", "-m", mensagem)
    sh("git", "-C", str(repo), "push", "-q", "-u", "origin", "develop")


def sync(repo: Path, perfil: str):
    print(sh(sys.executable, str(KIT / "sync.py"), "--repo", str(repo), "--perfil", perfil))


def criar(destino: Path):
    if destino.exists() and any(destino.iterdir()):
        sys.exit(f"ERRO: {destino} já existe e não está vazio. Use --limpar antes.")
    for ferramenta in ("git", "javac", "java"):
        if not shutil.which(ferramenta):
            sys.exit(f"ERRO: '{ferramenta}' não encontrado no PATH.")

    app = criar_repo(destino, "aplicacao-java")
    for nome, corpo in ANOTACOES.items():
        escrever(app, {f"src/main/java/sandbox/web/{nome}.java":
                       f"package sandbox.web;\n\nimport java.lang.annotation.*;\n\n{corpo}\n"})
    escrever(app, ARQUIVOS_APP)
    sync(app, "aplicacao")
    escrever(app, {"AGENTS.md": AGENTS_APP, ".harness/project.yaml": PROJECT_APP,
                   ".harness/sensores.json": SENSORES_APP, **DOCS_APP})
    gw = criar_repo(destino, "gateway-padrao")
    escrever(gw, {"openapi.yaml": CONTRATO, ".harness/validar_contrato.py": VALIDAR_CONTRATO})
    sync(gw, "gateway")
    escrever(gw, {"AGENTS.md": AGENTS_GW, ".harness/project.yaml": PROJECT_GW,
                  ".harness/sensores.json": SENSORES_GW})

    # O Claude Code só edita fora da pasta da sessão com additionalDirectories.
    escrever(app, {".claude/settings.local.json": {"permissions": {
        "additionalDirectories": [gw.as_posix()],
        "allow": ["Bash(python .harness/compilar.py)"]}}})

    r = subprocess.run([sys.executable, str(app / ".harness" / "compilar.py")], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ERRO: o Java do sandbox não compilou:\n{r.stdout}{r.stderr}")

    publicar(app, "sandbox: aplicação inicial")
    publicar(gw, "sandbox: contrato inicial")
    escrever(destino / "historias", {**HISTORIAS, "LEIA-ME.md": LEIA_ME})

    workspace = (f"{MARCA}\nrepos:\n  aplicacao-java: {app.as_posix()}\n"
                 f"  gateway-padrao: {gw.as_posix()}\n")
    if WORKSPACE.exists():
        print(f"\n{WORKSPACE} já existe e não foi alterado. Garanta que ele tenha:\n{workspace}")
    else:
        WORKSPACE.parent.mkdir(parents=True, exist_ok=True)
        WORKSPACE.write_text(workspace, encoding="utf-8")
        print(f"\nCriado {WORKSPACE}")

    print(f"\nSandbox pronto em {destino}\n"
          f"Próximo passo: abra o Claude Code em {app} e siga harness-kit/docs/testes.md.")


def _apagar_somente_leitura(func, caminho, _):
    os.chmod(caminho, stat.S_IWRITE)  # objetos do .git são read-only no Windows
    func(caminho)


def limpar(destino: Path):
    if destino.exists():
        try:
            shutil.rmtree(destino, onerror=_apagar_somente_leitura)
            print(f"Apagado {destino}")
        except PermissionError as e:
            print(f"Não consegui apagar {destino}: algo está usando a pasta "
                  f"(feche o Claude Code/terminal/IDE abertos nela e rode de novo).\n  {e}")
    runs = HARNESS / "runs"
    ativo = runs / "active.json"
    if ativo.exists() and json.loads(ativo.read_text(encoding="utf-8")).get("historia", "").startswith("SBX-"):
        ativo.unlink()
        print(f"Apagado {ativo}")
    for pasta in runs.glob("SBX-*"):
        shutil.rmtree(pasta)
        print(f"Apagado {pasta}")
    if WORKSPACE.exists() and WORKSPACE.read_text(encoding="utf-8").startswith(MARCA):
        WORKSPACE.unlink()
        print(f"Apagado {WORKSPACE}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--destino", required=True)
    p.add_argument("--limpar", action="store_true", help="apaga o sandbox e as execuções SBX-*")
    a = p.parse_args()
    destino = Path(a.destino).resolve()
    limpar(destino) if a.limpar else criar(destino)
