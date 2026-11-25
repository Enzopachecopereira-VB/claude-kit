#!/usr/bin/env python3
"""Engine estruturado do cerimonial de release. Chamado por release.sh.

Divisao de trabalho (deliberada):
  release.sh  -> resolucao do repo, guardas git, chamadas gh, dispatch, saida
  este arquivo -> ledger, changelog, notas, manifesto, scan de segredo, deteccao

Por que Python e nao jq: python3 ja e dependencia comum de harnesses de release,
enquanto jq nao esta garantido. Introduzir jq criaria dependencia nova sem ganho.

Tolerancia a variantes NAO e frouxidao: repositorios reais divergem no shape do
ledger, no formato do changelog e no manifesto. Um validador que so aceita um
formato nao valida nada, porque ninguem consegue adota-lo. Estrutura errada e ERRO; convencao
divergente e WARN, promovido a ERRO por --strict.

Somente stdlib. Compativel com Python 3.8+.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date as date_cls
from pathlib import Path

SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
UNRELEASED_RE = re.compile(r"^##\s+\[?Unreleased\]?", re.IGNORECASE | re.MULTILINE)

# Aceita: ## [1.2.3] - 2026-01-01 | ## 1.2.3 - 2026-01-01 | ## 1.2.3 — data
#         ## [1.2.3] | ## 1.2.3 | com sufixo livre depois da versao.
CHANGELOG_HEADING_RE = re.compile(
    r"^##\s+\[?(\d+\.\d+\.\d+)\]?(?:\s*[-\u2013\u2014]\s*\S.*)?\s*$", re.MULTILINE
)

LEDGER_REL = "docs/release/ledger.json"
NOTES_REL = "docs/release"
CHANGELOG_REL = "CHANGELOG.md"

# Aliases de campo aceitos (variacoes comuns entre repositorios).
NAME_KEYS = ("releaseName", "release_name")
EVIDENCE_KEYS = ("evidence", "evidence_path", "notes")

# Familias de segredo. O literal de cada padrao nunca casa consigo mesmo
# (o proximo caractere depois do prefixo e '[', fora de toda classe), por isso
# este arquivo nao se auto-acusa quando varrido.
SECRET_PATTERNS = (
    ("stripe-live", re.compile(r"sk_live_[A-Za-z0-9]{16,}")),
    ("anthropic", re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}")),
    ("openai", re.compile(r"sk-proj-[A-Za-z0-9_-]{16,}")),
    ("aws-akid", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github", re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}")),
    ("slack", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("google", re.compile(r"AIza[0-9A-Za-z_-]{30,}")),
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("bearer", re.compile(r"Bearer\s+[A-Za-z0-9_.=-]{25,}")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
)

MANIFESTS = (
    ("package.json", "json"),
    ("deno.json", "json"),
    ("composer.json", "json"),
    ("Cargo.toml", "toml"),
    ("pyproject.toml", "toml"),
    ("VERSION", "plain"),
)

MAX_SCAN_BYTES = 2_000_000

# Falso positivo universal, permitido por VALOR EXATO (nunca por caminho): esta
# e a chave-exemplo publicada na documentacao oficial da AWS, usada em material
# didatico no mundo inteiro. Allowlist de repo vive em .release.json.
BUILTIN_ALLOWLIST = frozenset({"AKIAIOSFODNN7EXAMPLE"})


# ---------------------------------------------------------------------------
# util


def git(repo, *args):
    proc = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True
    )
    return proc.stdout.strip() if proc.returncode == 0 else None


def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


class ConfigError(Exception):
    """`.release.json` invalido. Nunca degrada em silencio: config ilegivel que
    vira {} faz o validador checar outra coisa sem avisar."""


def confine(repo, rel, what):
    """Todo path de config e resolvido DENTRO da raiz. Sem isto, um
    `"ledger": "../outro-repo/docs/release/ledger.json"` faria o check passar
    lendo o contrato de outro repositorio: falso-verde por configuracao."""
    root = Path(repo).resolve()
    target = (root / rel).resolve()
    if target != root and root not in target.parents:
        raise ConfigError(f"{what} aponta para fora do repositorio: {rel}")
    return target


def load_config(repo):
    """`.release.json` opcional na raiz. Toda chave e override do detectado."""
    raw = read_text(Path(repo) / ".release.json")
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigError(f".release.json invalido: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(".release.json deve conter um objeto")
    for key, what in (("ledger", "ledger"), ("changelog", "changelog"),
                      ("notesDir", "notesDir")):
        if isinstance(data.get(key), str):
            confine(repo, data[key], what)
    if isinstance(data.get("manifest"), str):
        confine(repo, data["manifest"], "manifest")
    return data


def entry_get(entry, keys, default=None):
    for key in keys:
        if key in entry and entry[key] not in (None, ""):
            return entry[key]
    return default


# ---------------------------------------------------------------------------
# ledger


def ledger_path(repo, cfg):
    return Path(repo) / cfg.get("ledger", LEDGER_REL)


def load_ledger(repo, cfg):
    """Retorna (root, releases, erro). Aceita objeto com `releases` ou array."""
    path = ledger_path(repo, cfg)
    raw = read_text(path)
    if raw is None:
        return None, None, "ausente"
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, None, f"JSON invalido: {exc}"
    if isinstance(data, list):
        return {"releases": data}, data, None
    if isinstance(data, dict) and isinstance(data.get("releases"), list):
        return data, data["releases"], None
    return None, None, "raiz deve ser objeto com array `releases` (ou array)"


def save_ledger(repo, cfg, root):
    path = ledger_path(repo, cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(root, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# deteccao de convencoes


def detect_tag_prefix(repo, cfg, releases):
    if "tagPrefix" in cfg:
        return cfg["tagPrefix"]
    for entry in reversed(releases or []):
        version, tag = entry.get("version"), entry.get("tag")
        if isinstance(version, str) and isinstance(tag, str):
            if tag == version:
                return ""
            if tag == "v" + version:
                return "v"
    tags = (git(repo, "tag") or "").split()
    if any(re.match(r"^v\d+\.\d+\.\d+", t) for t in tags):
        return "v"
    if any(re.match(r"^\d+\.\d+\.\d+", t) for t in tags):
        return ""
    return "v"


def detect_name_style(repo, cfg, releases):
    """bare = X.Y.Z (o mais comum) | tag = vX.Y.Z | tag-desc = vX.Y.Z - texto."""
    if "releaseNameStyle" in cfg:
        return cfg["releaseNameStyle"]
    for entry in reversed(releases or []):
        name = entry_get(entry, NAME_KEYS)
        version, tag = entry.get("version"), entry.get("tag")
        if not isinstance(name, str) or not isinstance(version, str):
            continue
        if name == version:
            return "bare"
        if isinstance(tag, str) and name == tag:
            return "tag"
        if isinstance(tag, str) and name.startswith(tag) and len(name) > len(tag):
            return "tag-desc"
    return "bare"


def detect_manifest(repo, cfg):
    """Retorna (path_relativo, kind, versao) ou (None, None, None). Opcional."""
    if cfg.get("manifest") is False or cfg.get("noManifest"):
        return None, None, None
    candidates = [(cfg["manifest"], _kind_of(cfg["manifest"]))] if cfg.get("manifest") else MANIFESTS
    for rel, kind in candidates:
        path = Path(repo) / rel
        if not path.is_file():
            continue
        version = read_manifest_version(path, kind)
        if version:
            return rel, kind, version
    return None, None, None


def _kind_of(rel):
    if rel.endswith(".json"):
        return "json"
    if rel.endswith(".toml"):
        return "toml"
    return "plain"


def read_manifest_version(path, kind):
    raw = read_text(path)
    if raw is None:
        return None
    if kind == "json":
        try:
            value = json.loads(raw).get("version")
            return value if isinstance(value, str) else None
        except (json.JSONDecodeError, AttributeError):
            return None
    if kind == "toml":
        match = re.search(r'(?m)^\s*version\s*=\s*"([^"]+)"', raw)
        return match.group(1) if match else None
    stripped = raw.strip()
    return stripped if SEMVER_RE.match(stripped) else None


def _root_version_span(raw):
    """Posicao do valor da chave `version` de NIVEL RAIZ num JSON.

    Regex ingenua casaria `overrides.dep.version` quando ela vem antes da chave
    raiz, bumpando a dependencia e deixando o pacote na versao velha. Aqui a
    profundidade e contada de verdade, respeitando string e escape.
    """
    depth = 0
    i = 0
    in_str = False
    esc = False
    key_at_root = None
    while i < len(raw):
        ch = raw[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
            if depth == 1 and raw[i:i + 9] == chr(34) + "version" + chr(34):
                key_at_root = i
        elif ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
        elif ch == ":" and key_at_root is not None and depth == 1:
            j = i + 1
            while j < len(raw) and raw[j] in " \t\r\n":
                j += 1
            if j < len(raw) and raw[j] == '"':
                end = raw.index('"', j + 1)
                return j, end + 1
            key_at_root = None
        i += 1
    return None


def write_manifest_version(path, kind, version):
    raw = read_text(path)
    if raw is None:
        return False
    if kind == "json":
        span = _root_version_span(raw)
        if span is None:
            return False
        new = raw[: span[0]] + '"' + version + '"' + raw[span[1]:]
    elif kind == "toml":
        # Only inside the declaring table ([package] / [project] / [tool.poetry]).
        lines = raw.split("\n")
        section = ""
        done = False
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                section = stripped.strip("[]")
                continue
            if done or section not in ("package", "project", "tool.poetry"):
                continue
            m = re.match(r'^(\s*version\s*=\s*)"[^"]*"(.*)$', line)
            if m:
                lines[idx] = m.group(1) + '"' + version + '"' + m.group(2)
                done = True
        if not done:
            return False
        new = "\n".join(lines)
    else:
        new = version + "\n"
    Path(path).write_text(new, encoding="utf-8")
    return True


def detect(repo, cfg=None):
    cfg = cfg if cfg is not None else load_config(repo)
    _, releases, err = load_ledger(repo, cfg)
    releases = releases or []
    manifest, kind, mversion = detect_manifest(repo, cfg)
    prefix = detect_tag_prefix(repo, cfg, releases)
    ledger_versions = [e.get("version") for e in releases if isinstance(e.get("version"), str)]
    return {
        "repo": str(repo),
        "ledger": cfg.get("ledger", LEDGER_REL),
        "ledgerPresent": err is None,
        "ledgerError": err,
        "ledgerCount": len(releases),
        "notesDir": cfg.get("notesDir", NOTES_REL),
        "changelog": cfg.get("changelog", CHANGELOG_REL),
        "changelogPresent": (Path(repo) / cfg.get("changelog", CHANGELOG_REL)).is_file(),
        "tagPrefix": prefix,
        "releaseNameStyle": detect_name_style(repo, cfg, releases),
        "manifest": manifest,
        "manifestKind": kind,
        "manifestVersion": mversion,
        "currentVersion": mversion or (ledger_versions[-1] if ledger_versions else None),
        "lastLedgerVersion": ledger_versions[-1] if ledger_versions else None,
        "ciCommand": cfg.get("ciCommand"),
        "configPresent": bool(cfg),
    }


# ---------------------------------------------------------------------------
# changelog


def changelog_versions(text):
    return set(CHANGELOG_HEADING_RE.findall(text or ""))


def insert_changelog_section(text, version, day, heading_style):
    """Move o conteudo de Unreleased para a secao da versao, preservando ambos."""
    heading = (
        f"## [{version}] - {day}" if heading_style == "bracket" else f"## {version} - {day}"
    )
    match = UNRELEASED_RE.search(text)
    if not match:
        return text.rstrip("\n") + f"\n\n{heading}\n"
    start = match.end()
    nxt = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + nxt.start() if nxt else len(text)
    body = text[start:end].strip("\n")
    head = text[:start]
    tail = text[end:]
    block = f"\n\n{heading}\n\n{body}\n\n" if body else f"\n\n{heading}\n\n"
    return head + "\n\n" + block.strip("\n") + "\n\n" + tail.lstrip("\n")


def count_unreleased(text):
    return len(UNRELEASED_RE.findall(text or ""))


def detect_heading_style(text):
    for line in (text or "").splitlines():
        if CHANGELOG_HEADING_RE.match(line):
            return "bracket" if "[" in line else "plain"
    return "bracket"


def first_bullet(text, version):
    """Primeira linha de bullet da secao da versao: vira descricao do nome."""
    match = re.search(
        rf"^##\s+\[?{re.escape(version)}\]?.*$", text or "", re.MULTILINE
    )
    if not match:
        return None
    rest = text[match.end():]
    nxt = re.search(r"^##\s+", rest, re.MULTILINE)
    block = rest[: nxt.start()] if nxt else rest
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("- "):
            return re.sub(r"\s+", " ", line[2:]).strip().rstrip(".")
    return None


# ---------------------------------------------------------------------------
# notas


NOTE_TEMPLATE = """# {version}

Tag: `{tag}`
Release name: `{name}`
Date: {day}
Milestone: {milestone}

## Entregas

{body}

## Verificacao

- (registre aqui o que foi medido: comandos, exit codes, artefatos)

## Limitacoes conhecidas

- (o que esta release NAO resolve)
"""


def note_path(repo, cfg, version):
    return Path(repo) / cfg.get("notesDir", NOTES_REL) / f"{version}.md"


def render_note(version, tag, name, day, body, milestone="-"):
    return NOTE_TEMPLATE.format(
        version=version, tag=tag, name=name, day=day,
        milestone=milestone, body=body or "- (descreva a entrega)",
    )


# ---------------------------------------------------------------------------
# scan de segredo (no repo ALVO, sempre)


def tracked_files(repo):
    out = git(repo, "ls-files", "-z")
    if out is None:
        return None
    return [p for p in out.split("\0") if p]


def index_blob(repo, rel):
    """Conteudo do arquivo COMO ESTA NO INDICE (`git show :path`), em bytes.

    Ler o working tree seria errado num gate de pre-commit: `git add segredo` +
    sobrescrever o arquivo com conteudo limpo deixaria o blob comprometido no
    indice e o gate passaria. O que vai para o commit e o blob, nao o disco.
    """
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", ":" + rel], capture_output=True
    )
    return proc.stdout if proc.returncode == 0 else None


def scan_secrets(repo, allowlist):
    """Varre os BLOBS DO INDICE do repo alvo. Nada e pulado em silencio: o que
    nao pode ser varrido e devolvido em `skipped` e reportado ao usuario."""
    files = tracked_files(repo)
    if files is None:
        return None, None, ["nao e repositorio git ou git indisponivel"]
    permitted = set(allowlist) | BUILTIN_ALLOWLIST
    hits, skipped = [], []
    for rel in files:
        blob = index_blob(repo, rel)
        if blob is None:
            path = Path(repo) / rel
            try:
                blob = path.read_bytes()
            except OSError:
                skipped.append((rel, "ilegivel"))
                continue
        if len(blob) > MAX_SCAN_BYTES:
            skipped.append((rel, f"{len(blob)} bytes acima do limite"))
            continue
        # latin-1 nunca falha e preserva os bytes 1:1; os padroes sao ASCII,
        # entao binario e UTF-8 invalido tambem sao varridos em vez de pulados.
        text = blob.decode("latin-1")
        for label, pattern in SECRET_PATTERNS:
            for found in pattern.finditer(text):
                # Todos os matches, nao so o primeiro: com allowlist, parar no
                # primeiro esconderia um segredo real logo abaixo dele.
                if found.group(0) in permitted:
                    continue
                line = text[: found.start()].count("\n") + 1
                hits.append({"file": rel, "line": line, "kind": label})
                break
    return hits, skipped, []


def is_tracked(repo, rel):
    """Evidencia pode ser arquivo OU diretorio de artefatos: ha repositorios que
    apontam para um diretorio de evidencias por versao. Para diretorio, basta que
    o git rastreie algo dentro dele."""
    target = Path(repo) / rel
    if target.is_dir():
        out = git(repo, "ls-files", "--", str(rel).rstrip("/"))
        return bool(out)
    out = git(repo, "ls-files", "--error-unmatch", "--", str(rel))
    return out is not None


# ---------------------------------------------------------------------------
# check


def check(repo, strict=False):
    cfg = load_config(repo)
    info = detect(repo, cfg)
    errors, warns = [], []

    root, releases, err = load_ledger(repo, cfg)
    if err == "ausente":
        errors.append(f"{info['ledger']} ausente: sem registro canonico nao ha release auditavel")
        return info, errors, warns
    if err:
        errors.append(f"{info['ledger']}: {err}")
        return info, errors, warns

    changelog_file = Path(repo) / info["changelog"]
    changelog = read_text(changelog_file)
    if changelog is None:
        errors.append(f"{info['changelog']} ausente")
        changelog = ""
    elif count_unreleased(changelog) == 0:
        warns.append(f"{info['changelog']} sem secao Unreleased no topo")
    elif count_unreleased(changelog) > 1:
        errors.append(f"{info['changelog']} tem mais de uma secao Unreleased (ambiguo)")
    known = changelog_versions(changelog)

    seen, versions = set(), []
    for index, entry in enumerate(releases):
        where = f"entrada {index}"
        if not isinstance(entry, dict):
            errors.append(f"{where}: deve ser objeto")
            continue
        version = entry.get("version")
        if not isinstance(version, str) or not SEMVER_RE.match(version):
            errors.append(f"{where}: version fora de MAJOR.MINOR.PATCH ({version!r})")
            continue
        where = f"ledger {version}"
        if version in seen:
            errors.append(f"{where}: versao duplicada")
        seen.add(version)
        versions.append(version)

        tag = entry.get("tag")
        expected_tag = info["tagPrefix"] + version
        if not isinstance(tag, str):
            warns.append(f"{where}: sem campo tag (esperado {expected_tag})")
        elif tag != expected_tag:
            warns.append(f"{where}: tag {tag} diverge da convencao do repo ({expected_tag})")

        if entry_get(entry, NAME_KEYS) is None:
            warns.append(f"{where}: sem releaseName (convencao do repo: {info['releaseNameStyle']})")

        day = entry.get("date")
        if day is None:
            warns.append(f"{where}: sem campo date")
        elif not isinstance(day, str) or not DATE_RE.match(day):
            # Data que nao e data e dado quebrado, nao divergencia de convencao.
            errors.append(f"{where}: date deve ser YYYY-MM-DD (achado {day!r})")

        evidence = entry_get(entry, EVIDENCE_KEYS)
        if evidence is None:
            warns.append(f"{where}: sem evidencia (nota narrativa)")
        elif not (Path(repo) / evidence).exists():
            # Estrutura quebrada: o ledger APONTA para evidencia inexistente.
            errors.append(f"{where}: evidencia {evidence} nao existe")
        elif not is_tracked(repo, evidence):
            # Existe na maquina mas nao no versionamento: ninguem mais consegue
            # auditar. Escolha legitima do repo, entao WARN e nao ERRO.
            warns.append(f"{where}: evidencia {evidence} nao esta rastreada pelo git")

        if version not in known:
            warns.append(f"{where}: {info['changelog']} sem secao para {version}")

    orphans = sorted(known - set(versions))
    if orphans:
        warns.append(f"{info['changelog']} tem versoes fora do ledger: {', '.join(orphans)}")

    if info["manifest"] and versions:
        if info["manifestVersion"] != versions[-1]:
            warns.append(
                f"{info['manifest']} esta em {info['manifestVersion']} "
                f"e a ultima entrada do ledger e {versions[-1]}"
            )

    if strict:
        errors.extend(warns)
        warns = []
    return info, errors, warns


# ---------------------------------------------------------------------------
# comandos


def cmd_detect(args):
    print(json.dumps(detect(args.repo), ensure_ascii=False, indent=2))
    return 0


def cmd_check(args):
    info, errors, warns = check(args.repo, strict=args.strict)
    if args.json:
        print(json.dumps(
            {"repo": info["repo"], "errors": errors, "warnings": warns,
             "ok": not errors, "strict": args.strict},
            ensure_ascii=False, indent=2))
    else:
        for warn in warns:
            print(f"  WARN  {warn}")
        for error in errors:
            print(f"  ERRO  {error}")
        if not errors:
            print(f"  ok    contrato de release coerente "
                  f"({info['ledgerCount']} versoes no ledger, corrente: {info['currentVersion']})")
    return 1 if errors else 0


def cmd_init(args):
    repo = Path(args.repo)
    cfg = load_config(repo)
    created = []
    changelog = repo / cfg.get("changelog", CHANGELOG_REL)
    if not changelog.exists():
        changelog.write_text(
            "# Changelog\n\n"
            "Formato [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/);\n"
            "versionamento [SemVer](https://semver.org/lang/pt-BR/).\n\n"
            "Registro canonico das versoes publicadas: `docs/release/ledger.json`.\n\n"
            "## [Unreleased]\n",
            encoding="utf-8")
        created.append(str(changelog.relative_to(repo)))
    path = ledger_path(repo, cfg)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"schema": "git-pro/release-ledger@1", "releases": []}, indent=2) + "\n",
            encoding="utf-8")
        created.append(str(path.relative_to(repo)))
    notes = repo / cfg.get("notesDir", NOTES_REL)
    notes.mkdir(parents=True, exist_ok=True)
    for item in created:
        print(f"  criado  {item}")
    if not created:
        print("  ok    contrato ja existia (init e idempotente)")
    return 0


def cmd_prepare(args):
    repo = Path(args.repo)
    version = args.version
    if not SEMVER_RE.match(version):
        print(f"  ERRO  versao deve ser MAJOR.MINOR.PATCH sem prefixo (achado {version!r})")
        return 2
    cfg = load_config(repo)
    root, releases, err = load_ledger(repo, cfg)
    if err:
        print(f"  ERRO  {ledger_path(repo, cfg)}: {err} (rode `release.sh init`)")
        return 1
    if any(isinstance(e, dict) and e.get("version") == version for e in releases):
        print(f"  ERRO  {version} ja existe no ledger: versao publicada nao se reusa")
        return 1

    info = detect(repo, cfg)
    day = args.date or date_cls.today().isoformat()
    if not DATE_RE.match(day):
        print(f"  ERRO  --date deve ser YYYY-MM-DD (achado {day!r})")
        return 2
    tag = info["tagPrefix"] + version

    changelog_file = Path(repo) / info["changelog"]
    # read_bytes, nao read_text: universal newlines converteria CRLF em LF na
    # LEITURA, e a deteccao de convencao nunca veria o CRLF do arquivo.
    try:
        raw = changelog_file.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        raw = "# Changelog\n\n## [Unreleased]\n"
    # Preserva a convencao de fim de linha: reescrever CRLF como LF produz um
    # diff de arquivo inteiro que esconde a mudanca real.
    crlf = "\r\n" in raw
    text = raw.replace("\r\n", "\n")
    if count_unreleased(text) > 1:
        print("  ERRO  changelog tem mais de uma secao Unreleased: ambiguo, "
              "nao da para saber qual promover")
        return 1
    style = detect_heading_style(text)
    text = insert_changelog_section(text, version, day, style)
    changelog_file.write_bytes(
        (text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))

    if args.release_name:
        name = args.release_name
    elif info["releaseNameStyle"] == "tag":
        name = tag
    elif info["releaseNameStyle"] == "tag-desc":
        desc = first_bullet(text, version)
        name = f"{tag} - {desc}" if desc else tag
    else:
        name = version

    note = note_path(repo, cfg, version)
    if not note.exists():
        note.parent.mkdir(parents=True, exist_ok=True)
        bullets = []
        section = re.search(rf"^##\s+\[?{re.escape(version)}\]?.*$", text, re.MULTILINE)
        if section:
            rest = text[section.end():]
            nxt = re.search(r"^##\s+", rest, re.MULTILINE)
            bullets = [l for l in (rest[: nxt.start()] if nxt else rest).splitlines()
                       if l.strip().startswith("- ")]
        note.write_text(render_note(version, tag, name, day, "\n".join(bullets)), encoding="utf-8")

    entry = {
        "version": version,
        "tag": tag,
        "releaseName": name,
        "date": day,
        "evidence": str(note.relative_to(repo)),
    }
    releases.append(entry)
    root["releases"] = releases
    save_ledger(repo, cfg, root)

    if info["manifest"]:
        write_manifest_version(Path(repo) / info["manifest"], info["manifestKind"], version)
        print(f"  bump    {info['manifest']} -> {version}")
    print(f"  ok      {info['changelog']}, {entry['evidence']} e ledger atualizados ({tag})")
    print(f"  NEXT    revise a narrativa em {entry['evidence']}, commit, push, "
          f"e entao: release.sh publish {version}")
    return 0


def cmd_scan(args):
    cfg = load_config(args.repo)
    allowlist = set(cfg.get("secretAllowlist", []))
    hits, skipped, fatal = scan_secrets(args.repo, allowlist)
    for message in fatal:
        print(f"  ERRO  {message}")
    if fatal:
        return 2
    for rel, why in skipped or []:
        # Nunca contabilizar como limpo o que nao foi lido.
        print(f"  ERRO  nao varrido (revise a mao): {rel} ({why})")
    for hit in hits:
        print(f"  ERRO  possivel segredo [{hit['kind']}] em {hit['file']}:{hit['line']}")
    if hits or skipped:
        print("  Segredo que tocou commit esta QUEIMADO: rotacione. Remover do arquivo")
        print("  nao remove do historico. Falso positivo legitimo: allowlist por string")
        print("  exata em .release.json -> secretAllowlist (nunca silenciar por caminho).")
        return 1
    files = tracked_files(args.repo) or []
    print(f"  ok    anti-segredo: {len(files)} blobs do indice de {args.repo} limpos")
    return 0


def cmd_ledger_entry(args):
    """Imprime a entrada do ledger de uma versao (consumido pelo bash)."""
    cfg = load_config(args.repo)
    _, releases, err = load_ledger(args.repo, cfg)
    if err:
        print(json.dumps({"error": err}))
        return 1
    for entry in releases or []:
        if isinstance(entry, dict) and entry.get("version") == args.version:
            info = detect(args.repo, cfg)
            print(json.dumps({
                "version": entry.get("version"),
                "tag": entry.get("tag") or info["tagPrefix"] + args.version,
                "releaseName": entry_get(entry, NAME_KEYS) or entry.get("version"),
                "date": entry.get("date"),
                "evidence": entry_get(entry, EVIDENCE_KEYS),
                "isLast": releases[-1] is entry,
            }, ensure_ascii=False))
            return 0
    print(json.dumps({"error": f"versao {args.version} ausente do ledger"}))
    return 1


def main(argv=None):
    parser = argparse.ArgumentParser(prog="release_engine.py", add_help=True)
    sub = parser.add_subparsers(dest="cmd", required=True)

    for name in ("detect", "init", "scan"):
        node = sub.add_parser(name)
        node.add_argument("repo")

    node = sub.add_parser("check")
    node.add_argument("repo")
    node.add_argument("--strict", action="store_true")
    node.add_argument("--json", action="store_true")

    node = sub.add_parser("prepare")
    node.add_argument("repo")
    node.add_argument("version")
    node.add_argument("--date")
    node.add_argument("--release-name", dest="release_name")

    node = sub.add_parser("ledger-entry")
    node.add_argument("repo")
    node.add_argument("version")

    args = parser.parse_args(argv)
    handlers = {
        "detect": cmd_detect, "check": cmd_check, "init": cmd_init,
        "prepare": cmd_prepare, "scan": cmd_scan, "ledger-entry": cmd_ledger_entry,
    }
    try:
        return handlers[args.cmd](args)
    except ConfigError as exc:
        # Config quebrada nunca degrada em silencio: validar com defaults quando
        # o usuario pediu outra coisa e validar a coisa errada.
        print(f"  ERRO  {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
