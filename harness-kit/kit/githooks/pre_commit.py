"""Git pre-commit: rede final. Bloqueia commit fora de feature/<id> quando há
execução ativa do harness. Vale para Claude, Devin e commits manuais."""
import json
import os
import subprocess
import sys
from pathlib import Path

RUN_FILE = Path.home() / ".harness" / "runs" / "active.json"


def norm(p):
    return os.path.normcase(str(Path(p).resolve()))


if not RUN_FILE.exists():
    sys.exit(0)

run = json.loads(RUN_FILE.read_text(encoding="utf-8"))
raiz = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
if norm(raiz) not in {norm(r) for r in run["repos"]}:
    sys.exit(0)

branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True).stdout.strip()
esperado = f"feature/{run['historia']}"
if branch != esperado:
    print(f"Commit bloqueado: branch '{branch}', esperado '{esperado}'.", file=sys.stderr)
    sys.exit(1)
