#!/usr/bin/env python3
"""Suite do cerimonial de release portatil (skills/git-pro/scripts/release.sh).

Exercita a SUPERFICIE PUBLICA do script, nunca internals do engine: o contrato
que importa e o que um agente digita em qualquer um dos repos da maquina.

Sem dependencia externa: unittest da stdlib, repos git temporarios, e stubs de
`gh`/`gitleaks` injetados por PATH. Nenhum teste toca a rede.

NOTA DE SEGURANCA: os segredos de teste sao montados por CONCATENACAO em tempo
de execucao. O padrao literal NUNCA aparece neste arquivo, senao o scan
anti-segredo do proprio repo (src/ci.mjs, que varre todo arquivo rastreado)
acusaria este teste como vazamento.

    python3 skills/git-pro/scripts/test_release.py -v
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "release.sh"

GIT_ENV = {
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
}

GH_STUB = """#!/usr/bin/env bash
# stub de gh: responde sem rede. Registra a invocacao em $GH_STUB_LOG.
printf '%s\\n' "$*" >> "${GH_STUB_LOG:-/dev/null}"
case "$1 $2" in
  "release view")
    [ "${GH_STUB_RELEASE_EXISTS:-0}" = "1" ] && exit 0
    printf 'release not found\\n' >&2; exit 1 ;;
  "release create"|"release edit") exit 0 ;;
  "api "*|"api")
    # checks de CI remoto
    printf '%s\\n' "${GH_STUB_CHECKS_JSON:-{\\"check_runs\\":[]}}" ; exit 0 ;;
esac
exit 0
"""

GITLEAKS_STUB = """#!/usr/bin/env bash
printf '%s\\n' "$*" >> "${GITLEAKS_STUB_LOG:-/dev/null}"
exit "${GITLEAKS_STUB_EXIT:-0}"
"""


def _fake_secret(kind):
    """Monta segredo de teste sem que o literal exista no fonte."""
    if kind == "org":
        return "sk_" + "live_" + ("a1b2c3d4" * 3)
    if kind == "aws":
        return "AKI" + "A" + "ABCDEFGHIJKLMNOP"
    if kind == "anthropic":
        return "sk-" + "ant-" + ("x" * 24)
    raise AssertionError("kind desconhecido: " + kind)


class ReleaseCase(unittest.TestCase):
    """Base: monta um repo git real e descartavel, com remote bare local."""

    maxDiff = None

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        # .resolve(): em macOS o tempdir e /var/... mas `git rev-parse
        # --show-toplevel` devolve o path real /private/var/... . Sem canonizar
        # aqui, a comparacao de paths falharia por symlink, nao por defeito.
        self.root = Path(self._tmp.name).resolve()
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self._write_stub("gh", GH_STUB)
        self._write_stub("gitleaks", GITLEAKS_STUB)
        self.gh_log = self.root / "gh.log"
        self.env = dict(os.environ)
        self.env.update(GIT_ENV)
        self.env["PATH"] = str(self.bin) + os.pathsep + self.env["PATH"]
        self.env["GH_STUB_LOG"] = str(self.gh_log)
        self.git("init", "-q")
        self.git("symbolic-ref", "HEAD", "refs/heads/main")

    def tearDown(self):
        self._tmp.cleanup()

    # -- infra ---------------------------------------------------------------

    def _write_stub(self, name, body):
        path = self.bin / name
        path.write_text(body, encoding="utf-8")
        path.chmod(0o755)

    def git(self, *args, cwd=None):
        return subprocess.run(
            ["git", *args],
            cwd=str(cwd or self.repo),
            env=self.env,
            capture_output=True,
            text=True,
            check=True,
        )

    def commit(self, message="chore: init", **files):
        for name, body in (files or {"README.md": "# repo\n"}).items():
            target = self.repo / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def add_origin(self, url=None):
        """Remote bare local por padrao; url explicita para simular GitHub."""
        if url is None:
            bare = self.root / "origin.git"
            subprocess.run(
                ["git", "init", "--bare", "-q", str(bare)],
                env=self.env, check=True, capture_output=True,
            )
            url = str(bare)
        self.git("remote", "add", "origin", url)
        if not url.startswith("http"):
            self.git("push", "-q", "-u", "origin", "main")

    def run_release(self, *args, cwd=None):
        return subprocess.run(
            ["bash", str(SCRIPT), *args],
            cwd=str(cwd or self.repo),
            env=self.env,
            capture_output=True,
            text=True,
        )

    def read_ledger(self):
        return json.loads((self.repo / "docs/release/ledger.json").read_text("utf-8"))

    def write_ledger(self, payload):
        path = self.repo / "docs/release/ledger.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def seed_release_contract(self, releases):
        self.commit()
        self.write_ledger({"releases": releases})
        changelog_sections = ["# Changelog", "", "## [Unreleased]", ""]
        for entry in releases:
            version = entry["version"]
            changelog_sections.extend([
                f"## [{version}] - {entry['date']}", "", "- x", "",
            ])
            evidence = entry.get("evidence") or entry.get("evidence_path") or entry.get("notes")
            note = self.repo / evidence
            note.parent.mkdir(parents=True, exist_ok=True)
            note.write_text(
                f"# {version}\n\nTag: `{entry['tag']}`\nDate: {entry['date']}\nMilestone: -\n\n- x\n",
                encoding="utf-8",
            )
        (self.repo / "CHANGELOG.md").write_text("\n".join(changelog_sections), encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "chore: seed release contract")

    def assertOk(self, proc, msg=""):
        self.assertEqual(
            proc.returncode, 0,
            f"{msg}\nexit={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
        )

    def assertFails(self, proc, msg=""):
        self.assertNotEqual(
            proc.returncode, 0,
            f"{msg} (esperava falha)\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
        )

    def bootstrap(self, version="1.0.0"):
        """Repo com contrato ja inicializado e uma release publicada."""
        self.commit()
        self.add_origin()
        self.assertOk(self.run_release("init"), "init de bootstrap")
        self.assertOk(self.run_release("prepare", version), "prepare de bootstrap")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", f"chore(release): {version}")
        self.git("push", "-q", "origin", "main")


# ---------------------------------------------------------------------------
# S1 — init em repo virgem
# ---------------------------------------------------------------------------

class S1Init(ReleaseCase):
    def test_s1_init_creates_contract_and_check_passes(self):
        self.commit()
        proc = self.run_release("init")
        self.assertOk(proc, "init deve criar o contrato")
        self.assertTrue((self.repo / "CHANGELOG.md").is_file(), "CHANGELOG.md ausente")
        ledger = self.repo / "docs/release/ledger.json"
        self.assertTrue(ledger.is_file(), "ledger.json ausente")
        data = json.loads(ledger.read_text("utf-8"))
        self.assertIn("releases", data, "ledger sem chave releases")
        self.assertEqual(data["releases"], [], "ledger novo deve nascer vazio")
        self.assertIn("## [Unreleased]", (self.repo / "CHANGELOG.md").read_text("utf-8"))
        self.assertOk(self.run_release("check"), "check apos init deve passar")

    def test_s1_init_is_idempotent_and_preserves_content(self):
        self.commit()
        self.assertOk(self.run_release("init"))
        (self.repo / "CHANGELOG.md").write_text(
            "# Changelog\n\n## [Unreleased]\n\n### Added\n- coisa minha\n", encoding="utf-8"
        )
        self.assertOk(self.run_release("init"), "init repetido nao pode falhar")
        self.assertIn("coisa minha", (self.repo / "CHANGELOG.md").read_text("utf-8"),
                      "init sobrescreveu conteudo do usuario")


# ---------------------------------------------------------------------------
# S2 — prepare
# ---------------------------------------------------------------------------

class S2Prepare(ReleaseCase):
    def test_s2_prepare_updates_changelog_note_ledger_and_manifest(self):
        self.commit(**{"package.json": json.dumps({"name": "x", "version": "0.9.0"}) + "\n"})
        self.assertOk(self.run_release("init"))
        (self.repo / "CHANGELOG.md").write_text(
            "# Changelog\n\n## [Unreleased]\n\n### Added\n- feature nova\n", encoding="utf-8"
        )
        proc = self.run_release("prepare", "1.0.0")
        self.assertOk(proc, "prepare deve montar os artefatos")

        changelog = (self.repo / "CHANGELOG.md").read_text("utf-8")
        self.assertIn("## [Unreleased]", changelog, "Unreleased deve permanecer no topo")
        self.assertIn("## [1.0.0]", changelog, "secao da versao nao criada")
        self.assertIn("feature nova", changelog, "conteudo do Unreleased foi perdido")
        self.assertLess(changelog.index("## [Unreleased]"), changelog.index("## [1.0.0]"),
                        "Unreleased tem que ficar ACIMA da versao")

        note = self.repo / "docs/release/1.0.0.md"
        self.assertTrue(note.is_file(), "nota narrativa nao criada")
        body = note.read_text("utf-8")
        for fragment in ("# 1.0.0", "Tag:", "Date:"):
            self.assertIn(fragment, body, f"nota sem campo {fragment}")

        entry = self.read_ledger()["releases"][-1]
        self.assertEqual(entry["version"], "1.0.0")
        self.assertEqual(entry["tag"], "v1.0.0")

        manifest = json.loads((self.repo / "package.json").read_text("utf-8"))
        self.assertEqual(manifest["version"], "1.0.0", "manifest nao foi bumpado")
        self.assertOk(self.run_release("check"), "check apos prepare deve passar")

    def test_s2_prepare_refuses_duplicate_version(self):
        self.commit()
        self.assertOk(self.run_release("init"))
        self.assertOk(self.run_release("prepare", "1.0.0"))
        self.assertFails(self.run_release("prepare", "1.0.0"),
                         "reusar versao do ledger tem que ser recusado")

    def test_s2_prepare_refuses_non_semver(self):
        self.commit()
        self.assertOk(self.run_release("init"))
        self.assertFails(self.run_release("prepare", "v1.0.0"), "prefixo v no argumento")
        self.assertFails(self.run_release("prepare", "1.0"), "semver incompleto")


# ---------------------------------------------------------------------------
# S3 / S6 / S7 — publish e suas guardas
# ---------------------------------------------------------------------------

class S3Publish(ReleaseCase):
    def test_s3_publish_dry_run_passes_without_creating_tag(self):
        self.bootstrap("1.0.0")
        proc = self.run_release("publish", "1.0.0", "--dry-run")
        self.assertOk(proc, "dry-run em main limpa e sincronizada deve passar")
        tags = self.git("tag").stdout.split()
        self.assertEqual(tags, [], "dry-run NAO pode criar tag")
        self.assertFalse(self.gh_log.exists() and "release create" in self.gh_log.read_text(),
                         "dry-run NAO pode chamar gh release create")

    def test_s7_publish_refuses_dirty_worktree(self):
        self.bootstrap("1.0.0")
        (self.repo / "sujeira.txt").write_text("x", encoding="utf-8")
        proc = self.run_release("publish", "1.0.0", "--dry-run")
        self.assertFails(proc, "worktree suja")
        self.assertIn("worktree suja", (proc.stdout + proc.stderr).lower(),
                      "a recusa tem que nomear a causa")

    def test_s6_publish_refuses_tag_on_different_commit(self):
        self.bootstrap("1.0.0")
        self.git("tag", "-a", "v1.0.0", "-m", "tag antiga", "HEAD~1")
        proc = self.run_release("publish", "1.0.0", "--dry-run")
        self.assertFails(proc, "tag existente apontando para outro commit")
        self.assertIn("HEAD", proc.stdout + proc.stderr)

    def test_s6_publish_accepts_tag_already_on_head(self):
        self.bootstrap("1.0.0")
        self.git("tag", "-a", "v1.0.0", "-m", "ja correta")
        self.assertOk(self.run_release("publish", "1.0.0", "--dry-run"),
                      "tag ja no HEAD e reuso legitimo, nao erro")

    def test_s3_publish_refuses_wrong_branch(self):
        self.bootstrap("1.0.0")
        self.git("checkout", "-q", "-b", "feature/x")
        self.assertFails(self.run_release("publish", "1.0.0", "--dry-run"),
                         "publicar fora da branch base")

    def test_s3_publish_refuses_version_not_last_in_ledger(self):
        self.bootstrap("1.0.0")
        self.assertFails(self.run_release("publish", "9.9.9", "--dry-run"),
                         "versao ausente do ledger")


# ---------------------------------------------------------------------------
# S4 / S5 — tolerancia a variantes reais de ledger
# ---------------------------------------------------------------------------

class S4Variants(ReleaseCase):
    def _seed(self, payload, note_name="1.0.0.md", note_version="1.0.0"):
        self.commit()
        self.write_ledger(payload)
        (self.repo / "CHANGELOG.md").write_text(
            f"# Changelog\n\n## [Unreleased]\n\n## [{note_version}] - 2026-07-24\n\n- x\n",
            encoding="utf-8",
        )
        note = self.repo / "docs/release" / note_name
        note.write_text(
            f"# {note_version}\n\nTag: `v{note_version}`\nDate: 2026-07-24\nMilestone: -\n\n- x\n",
            encoding="utf-8",
        )

    def test_s4_schema_key_variant_is_accepted(self):
        # shape {$schema, releases} com releaseName / evidence
        self._seed({
            "$schema": "./ledger.schema.json",
            "releases": [{
                "version": "1.0.0", "tag": "v1.0.0", "releaseName": "1.0.0",
                "date": "2026-07-24", "evidence": "docs/release/1.0.0.md",
            }],
        })
        self.assertOk(self.run_release("check"), "shape {$schema,releases} tem que passar")

    def test_s4_project_key_variant_with_notes_field(self):
        # shape {project, releases}: usa `notes` e `commit`, nao `evidence`
        self._seed({
            "project": "example-web",
            "releases": [{
                "version": "1.0.0", "tag": "v1.0.0", "date": "2026-07-24",
                "commit": "0" * 40, "notes": "docs/release/1.0.0.md",
            }],
        })
        proc = self.run_release("check")
        self.assertOk(proc, "shape {project,releases} com notes tem que passar")

    def test_s4_snake_case_variant_is_accepted(self):
        # shape snake_case: release_name / evidence_path
        self._seed({
            "schema_version": 1,
            "releases": [{
                "version": "1.0.0", "tag": "v1.0.0", "release_name": "1.0.0",
                "date": "2026-07-24", "evidence_path": "docs/release/1.0.0.md",
                "artifacts": {}, "counts": {}, "known_limitations": [],
            }],
        })
        self.assertOk(self.run_release("check"), "shape snake_case tem que passar")

    def test_s4_empty_ledger_is_valid_draft(self):
        self.commit()
        self.write_ledger({"$schema": "x", "releases": []})
        (self.repo / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n", encoding="utf-8")
        self.assertOk(self.run_release("check"), "ledger vazio e rascunho valido, nao erro")

    def test_s4_directory_evidence_is_accepted(self):
        # alguns repos apontam a evidencia para um DIRETORIO de artefatos,
        # nao para um .md. Exigir arquivo quebrava um repo que esta correto.
        self._seed({
            "schema_version": 1,
            "releases": [{
                "version": "1.0.0", "tag": "v1.0.0", "release_name": "1.0.0",
                "date": "2026-07-24", "evidence_path": "evidence/v1.0.0/",
            }],
        })
        (self.repo / "evidence/v1.0.0").mkdir(parents=True)
        (self.repo / "evidence/v1.0.0/prova.txt").write_text("x", encoding="utf-8")
        proc = self.run_release("check")
        self.assertOk(proc, "evidencia em diretorio existente e valida")

    def test_s4_untracked_evidence_warns(self):
        # Evidencia fora do versionamento nao e auditavel por terceiros: WARN,
        # nao ERRO (o repo pode ter escolhido isso deliberadamente).
        self._seed({
            "releases": [{
                "version": "1.0.0", "tag": "v1.0.0", "releaseName": "1.0.0",
                "date": "2026-07-24", "evidence": "local/1.0.0.md",
            }],
        })
        (self.repo / "local").mkdir()
        (self.repo / "local/1.0.0.md").write_text("# 1.0.0\n", encoding="utf-8")
        (self.repo / ".gitignore").write_text("local/\n", encoding="utf-8")
        proc = self.run_release("check")
        self.assertOk(proc, "evidencia untracked nao invalida a release")
        self.assertIn("WARN", proc.stdout + proc.stderr)
        self.assertIn("rastread", (proc.stdout + proc.stderr).lower(),
                      "o WARN tem que explicar que a evidencia nao esta versionada")

    def test_s5_missing_release_name_is_warning_not_error(self):
        self._seed({
            "releases": [{
                "version": "1.0.0", "tag": "v1.0.0", "date": "2026-07-24",
                "evidence": "docs/release/1.0.0.md",
            }],
        })
        proc = self.run_release("check")
        self.assertOk(proc, "releaseName ausente e convergencia, nao ruptura")
        self.assertIn("WARN", proc.stdout + proc.stderr, "faltou avisar sobre releaseName")

    def test_s5_strict_mode_promotes_warning_to_error(self):
        self._seed({
            "releases": [{
                "version": "1.0.0", "tag": "v1.0.0", "date": "2026-07-24",
                "evidence": "docs/release/1.0.0.md",
            }],
        })
        self.assertFails(self.run_release("check", "--strict"),
                         "--strict tem que promover WARN a erro")

    def test_s4_missing_note_is_always_an_error(self):
        self._seed({
            "releases": [{
                "version": "1.0.0", "tag": "v1.0.0", "releaseName": "1.0.0",
                "date": "2026-07-24", "evidence": "docs/release/1.0.0.md",
            }],
        })
        (self.repo / "docs/release/1.0.0.md").unlink()
        self.assertFails(self.run_release("check"), "nota ausente e erro em qualquer modo")


# ---------------------------------------------------------------------------
# S8 / S9 — deteccao de convencoes do repo
# ---------------------------------------------------------------------------

class S8Detection(ReleaseCase):
    def test_s8_detects_bare_tag_prefix_from_history(self):
        self.commit()
        self.git("tag", "-a", "0.9.0", "-m", "sem prefixo")
        self.assertOk(self.run_release("init"))
        self.assertOk(self.run_release("prepare", "1.0.0"))
        entry = self.read_ledger()["releases"][-1]
        self.assertEqual(entry["tag"], "1.0.0",
                         "repo com tags bare nao pode receber prefixo v a forca")

    def test_s8_defaults_to_v_prefix_without_history(self):
        self.commit()
        self.assertOk(self.run_release("init"))
        self.assertOk(self.run_release("prepare", "1.0.0"))
        self.assertEqual(self.read_ledger()["releases"][-1]["tag"], "v1.0.0")

    def test_s9_detects_version_file_manifest(self):
        self.commit(**{"VERSION": "0.9.0\n"})
        self.assertOk(self.run_release("init"))
        self.assertOk(self.run_release("prepare", "1.0.0"))
        self.assertEqual((self.repo / "VERSION").read_text("utf-8").strip(), "1.0.0")

    def test_s9_detects_cargo_manifest(self):
        self.commit(**{"Cargo.toml": '[package]\nname = "x"\nversion = "0.9.0"\n'})
        self.assertOk(self.run_release("init"))
        self.assertOk(self.run_release("prepare", "1.0.0"))
        self.assertIn('version = "1.0.0"', (self.repo / "Cargo.toml").read_text("utf-8"))

    def test_s9_absent_manifest_is_fine(self):
        # repos de skills/agentes costumam nao ter manifesto nenhum
        self.commit()
        self.assertOk(self.run_release("init"))
        self.assertOk(self.run_release("prepare", "1.0.0"), "repo sem manifesto deve funcionar")
        self.assertOk(self.run_release("check"))

    def test_s9_release_name_style_follows_existing_ledger(self):
        self.commit()
        self.write_ledger({"releases": [{
            "version": "0.9.0", "tag": "v0.9.0", "releaseName": "v0.9.0 - primeira",
            "date": "2026-07-01", "evidence": "docs/release/0.9.0.md",
        }]})
        (self.repo / "docs/release/0.9.0.md").write_text(
            "# 0.9.0\n\nTag: `v0.9.0`\nDate: 2026-07-01\nMilestone: -\n", encoding="utf-8")
        (self.repo / "CHANGELOG.md").write_text(
            "# Changelog\n\n## [Unreleased]\n\n## [0.9.0] - 2026-07-01\n", encoding="utf-8")
        self.assertOk(self.run_release("prepare", "1.0.0"))
        name = self.read_ledger()["releases"][-1].get("releaseName", "")
        self.assertTrue(name.startswith("v1.0.0"),
                        f"estilo tag-descricao do repo nao foi seguido: {name!r}")


# ---------------------------------------------------------------------------
# S10 — REGRESSAO do falso-verde (validar o repo ERRADO)
# ---------------------------------------------------------------------------

class S10RepoTargeting(ReleaseCase):
    def test_s10_repo_flag_targets_outer_repo_from_inner_repo_cwd(self):
        self.bootstrap("1.0.0")
        outsider = self.root / "outro"
        outsider.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=str(outsider), env=self.env, check=True)
        (outsider / "a.txt").write_text("x", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=str(outsider), env=self.env, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "x"], cwd=str(outsider),
                       env=self.env, check=True)

        proc = self.run_release("check", "--repo", str(self.repo), cwd=outsider)
        self.assertOk(proc, "--repo tem que mandar sobre o cwd")
        self.assertIn(str(self.repo), proc.stdout,
                      "a raiz resolvida TEM que aparecer na saida (anti falso-verde)")

    def test_s10_without_repo_flag_uses_cwd_repo_not_script_location(self):
        # Sem --repo, o alvo e o repo do CWD. O script mora em outro repo
        # (agents-harness); um repo virgem sem contrato tem que FALHAR aqui,
        # provando que ele nao validou a arvore de onde o script mora.
        self.commit()
        proc = self.run_release("check")
        self.assertFails(proc, "repo sem contrato deve falhar, nao herdar o do script")
        self.assertIn(str(self.repo), proc.stdout + proc.stderr,
                      "saida tem que nomear o repo avaliado")

    def test_s10_check_prints_resolved_root_on_success(self):
        self.bootstrap("1.0.0")
        proc = self.run_release("check")
        self.assertOk(proc)
        self.assertIn(str(self.repo), proc.stdout,
                      "sucesso sem dizer QUAL repo passou e falso-verde em potencial")


# ---------------------------------------------------------------------------
# S13 — gate anti-segredo le o repo ALVO
# ---------------------------------------------------------------------------

class S13SecretGate(ReleaseCase):
    def test_s13_gate_refuses_planted_secret_in_target_repo(self):
        self.commit(**{"config.yml": "token: " + _fake_secret("org") + "\n"})
        proc = self.run_release("gate")
        self.assertFails(proc, "segredo plantado tem que ser recusado")
        self.assertIn("config.yml", proc.stdout + proc.stderr,
                      "o gate tem que nomear o arquivo ofensor")

    def test_s13_gate_detects_multiple_families(self):
        for kind, name in (("aws", "aws.txt"), ("anthropic", "an.txt")):
            with self.subTest(kind=kind):
                self.setUp()
                self.commit(**{name: "k=" + _fake_secret(kind) + "\n"})
                self.assertFails(self.run_release("gate"), f"familia {kind} nao detectada")

    def test_s13_gate_passes_clean_repo_and_names_it(self):
        self.commit()
        proc = self.run_release("gate")
        self.assertOk(proc, "repo limpo deve passar")
        self.assertIn(str(self.repo), proc.stdout, "gate tem que dizer QUAL arvore leu")

    def test_s13_gate_scans_staged_new_file(self):
        self.commit()
        (self.repo / "novo.env").write_text("k=" + _fake_secret("org") + "\n", encoding="utf-8")
        self.git("add", "novo.env")
        self.assertFails(self.run_release("gate"),
                         "arquivo novo apenas staged tem que ser varrido (gate de pre-commit)")

    def test_s13_publish_runs_the_gate(self):
        self.bootstrap("1.0.0")
        (self.repo / "leak.txt").write_text("k=" + _fake_secret("org") + "\n", encoding="utf-8")
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "chore: leak")
        self.git("push", "-q", "origin", "main")
        self.assertFails(self.run_release("publish", "1.0.0", "--dry-run"),
                         "publish tem que rodar o gate anti-segredo")


# ---------------------------------------------------------------------------
# status / json — superficie de orientacao barata para o agente
# ---------------------------------------------------------------------------

class StatusSurface(ReleaseCase):
    def test_status_reports_missing_contract_without_failing(self):
        self.commit()
        proc = self.run_release("status")
        self.assertOk(proc, "status e orientacao: nunca falha por contrato ausente")
        self.assertIn(str(self.repo), proc.stdout)

    def test_status_json_is_machine_readable(self):
        self.bootstrap("1.0.0")
        proc = self.run_release("status", "--json")
        self.assertOk(proc)
        data = json.loads(proc.stdout)
        self.assertEqual(data["repo"], str(self.repo))
        for key in ("tagPrefix", "manifest", "ledger", "currentVersion"):
            self.assertIn(key, data, f"status --json sem chave {key}")

    def test_publish_emits_json_summary_for_release_record(self):
        self.bootstrap("1.0.0")
        proc = self.run_release("publish", "1.0.0", "--dry-run", "--json")
        self.assertOk(proc)
        data = json.loads(proc.stdout)
        for key in ("version", "tag", "commit", "repo", "dryRun"):
            self.assertIn(key, data, f"resumo sem chave {key}")
        self.assertTrue(data["dryRun"])


# ---------------------------------------------------------------------------
# Regressao dos bloqueadores encontrados em review adversarial.
# Cada teste nomeia o defeito que ele impede de voltar.
# ---------------------------------------------------------------------------

class ReviewBlockers(ReleaseCase):
    def test_b2_config_cannot_point_outside_the_repo(self):
        # Ledger de OUTRO repo faria o check passar validando o contrato alheio:
        # falso-verde por configuracao.
        self.bootstrap("1.0.0")
        outside = self.root / "alheio"
        outside.mkdir()
        (outside / "ledger.json").write_text('{"releases": []}', encoding="utf-8")
        (self.repo / ".release.json").write_text(
            json.dumps({"ledger": "../alheio/ledger.json"}), encoding="utf-8")
        proc = self.run_release("check")
        self.assertFails(proc, "config apontando para fora da raiz")
        self.assertIn("fora do repositorio", proc.stdout + proc.stderr)

    def test_b2_broken_config_is_error_not_silent_default(self):
        self.bootstrap("1.0.0")
        (self.repo / ".release.json").write_text("{ isso nao e json", encoding="utf-8")
        proc = self.run_release("check")
        self.assertFails(proc, "config ilegivel nao pode virar {} em silencio")
        self.assertIn("invalido", proc.stdout + proc.stderr)

    def test_b3_gate_reads_index_blob_not_working_tree(self):
        # `git add segredo` + sobrescrever o arquivo limpo no disco deixava o
        # blob comprometido no indice, e o gate passava.
        self.commit()
        leak = self.repo / "conf.yml"
        leak.write_text("token: " + _fake_secret("org") + "\n", encoding="utf-8")
        self.git("add", "conf.yml")
        leak.write_text("token: PLACEHOLDER\n", encoding="utf-8")
        proc = self.run_release("gate")
        self.assertFails(proc, "o que vai para o commit e o blob do indice")
        self.assertIn("conf.yml", proc.stdout + proc.stderr)

    def test_b4_unscannable_file_is_never_counted_as_clean(self):
        self.commit()
        big = self.repo / "grande.bin"
        big.write_bytes(b"x" * 2_100_000)
        self.git("add", "grande.bin")
        proc = self.run_release("gate")
        self.assertFails(proc, "arquivo nao varrido nao pode contar como limpo")
        self.assertIn("nao varrido", proc.stdout + proc.stderr)

    def test_b4_binary_file_is_scanned_not_skipped(self):
        self.commit()
        blob = b"\xff\xfe\x00binario " + _fake_secret("org").encode() + b"\n"
        (self.repo / "bin.dat").write_bytes(blob)
        self.git("add", "bin.dat")
        self.assertFails(self.run_release("gate"),
                         "UTF-8 invalido nao pode virar buraco no gate")

    def test_b5_allowlist_does_not_hide_a_second_secret(self):
        self.commit()
        permitted = _fake_secret("org")
        other = "sk_" + "live_" + ("9f8e7d6c" * 3)
        (self.repo / "dois.yml").write_text(
            f"a: {permitted}\nb: {other}\n", encoding="utf-8")
        (self.repo / ".release.json").write_text(
            json.dumps({"secretAllowlist": [permitted]}), encoding="utf-8")
        self.git("add", "-A")
        self.assertFails(self.run_release("gate"),
                         "parar no primeiro match escondia o segredo seguinte")

    def test_b6_nested_tag_does_not_satisfy_exact_tag(self):
        # `ls-remote --tags origin v1.0.0` casa por PADRAO e pegava foo/v1.0.0.
        self.bootstrap("1.0.0")
        bare = self.root / "origin.git"
        self.git("tag", "-a", "foo/v1.0.0", "-m", "aninhada")
        self.git("push", "-q", "origin", "foo/v1.0.0")
        self.git("tag", "-d", "foo/v1.0.0")
        proc = self.run_release("publish", "1.0.0", "--dry-run")
        self.assertOk(proc, "tag aninhada nao e a tag exata; nao deve interferir")
        self.assertTrue(bare.exists())

    def test_b7_dry_run_does_not_mutate_local_refs(self):
        self.bootstrap("1.0.0")
        fetch_head = self.repo / ".git/FETCH_HEAD"
        before = fetch_head.exists()
        self.assertOk(self.run_release("publish", "1.0.0", "--dry-run"))
        self.assertEqual(fetch_head.exists(), before,
                         "dry-run escreveu FETCH_HEAD: isso e mutacao")

    def test_b8_invalid_date_is_error_in_every_mode(self):
        self.bootstrap("1.0.0")
        ledger = self.read_ledger()
        ledger["releases"][-1]["date"] = "nao-e-data"
        self.write_ledger(ledger)
        self.assertFails(self.run_release("check"),
                         "data que nao e data e dado quebrado, nao convencao")

    def test_b10_bump_hits_root_version_not_nested_one(self):
        # `overrides.dep.version` antes da chave raiz fazia o bump acertar a
        # dependencia e deixar o pacote na versao velha.
        manifest = {
            "name": "x",
            "overrides": {"dep": {"version": "0.0.1"}},
            "version": "0.9.0",
        }
        self.commit(**{"package.json": json.dumps(manifest, indent=2) + "\n"})
        self.assertOk(self.run_release("init"))
        self.assertOk(self.run_release("prepare", "1.0.0"))
        got = json.loads((self.repo / "package.json").read_text("utf-8"))
        self.assertEqual(got["version"], "1.0.0", "versao da raiz nao foi bumpada")
        self.assertEqual(got["overrides"]["dep"]["version"], "0.0.1",
                         "bump corrompeu a versao de uma dependencia")

    def test_b11_crlf_changelog_stays_crlf(self):
        self.commit()
        self.assertOk(self.run_release("init"))
        (self.repo / "CHANGELOG.md").write_bytes(
            b"# Changelog\r\n\r\n## [Unreleased]\r\n\r\n- item\r\n")
        self.assertOk(self.run_release("prepare", "1.0.0"))
        raw = (self.repo / "CHANGELOG.md").read_bytes()
        self.assertIn(b"\r\n", raw, "CRLF virou LF: diff de arquivo inteiro")

    def test_b11_ambiguous_unreleased_is_refused(self):
        self.commit()
        self.assertOk(self.run_release("init"))
        (self.repo / "CHANGELOG.md").write_text(
            "# Changelog\n\n## [Unreleased]\n\n- a\n\n## Unreleased notas\n\n- b\n",
            encoding="utf-8")
        self.assertFails(self.run_release("prepare", "1.0.0"),
                         "duas secoes Unreleased: nao da para saber qual promover")

    def test_b12_date_argument_cannot_inject_another_flag(self):
        self.commit()
        self.assertOk(self.run_release("init"))
        proc = self.run_release(
            "prepare", "1.0.0", "--date", "2026-07-24 --release-name injetado")
        self.assertFails(proc, "argumento de data nao pode carregar outra flag")

    def test_b15_json_is_refused_where_there_is_no_payload(self):
        self.commit()
        for sub in ("init", "gate"):
            with self.subTest(sub=sub):
                proc = self.run_release(sub, "--json")
                self.assertFails(proc, f"{sub} --json devolvia texto humano no stdout")

    def test_b9_publish_accepts_directory_evidence_like_check_does(self):
        self.bootstrap("1.0.0")
        evid = self.repo / "docs/release/dir-1.0.0"
        evid.mkdir(parents=True)
        (evid / "nota.md").write_text("# 1.0.0\n\ncorpo\n", encoding="utf-8")
        ledger = self.read_ledger()
        ledger["releases"][-1]["evidence"] = "docs/release/dir-1.0.0"
        self.write_ledger(ledger)
        (self.repo / "docs/release/1.0.0.md").unlink()
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "chore: evidencia em diretorio")
        self.git("push", "-q", "origin", "main")
        self.assertOk(self.run_release("publish", "1.0.0", "--dry-run"),
                      "check aceitava diretorio e publish recusava: contrato quebrado")


if __name__ == "__main__":
    if not SCRIPT.exists():
        raise SystemExit(f"RED: {SCRIPT} ainda nao existe")
    if shutil.which("git") is None:
        raise SystemExit("git ausente")
    unittest.main(verbosity=2)
