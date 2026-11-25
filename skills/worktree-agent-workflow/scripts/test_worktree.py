#!/usr/bin/env python3
"""Testes do worktree.sh — guardas fail-closed, cascata de provas, ancoras.

Roda em repos git temporarios com WT_BASE isolado; sem rede (origem e um
bare repo local, entao a prova pr-merged fica naturalmente indisponivel e a
cascata degrada para as provas locais — o comportamento de producao offline).
"""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "worktree.sh"


def run(cmd, cwd, env=None, check=True):
    e = os.environ.copy()
    e.update(env or {})
    p = subprocess.run(cmd, cwd=str(cwd), env=e, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise AssertionError(
            f"cmd {cmd} rc={p.returncode}\nstdout:\n{p.stdout}\nstderr:\n{p.stderr}"
        )
    return p


def git(args, cwd, **kw):
    return run(["git"] + args, cwd, **kw)


class WtCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="wt-test-"))
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.wtbase = self.tmp / "wt"
        git(["init", "-q", "-b", "main", "."], self.repo)
        git(["config", "user.email", "t@t"], self.repo)
        git(["config", "user.name", "t"], self.repo)
        (self.repo / "a.txt").write_text("a\n")
        git(["add", "."], self.repo)
        git(["commit", "-qm", "base"], self.repo)
        self.env = {"WT_BASE": str(self.wtbase)}

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- helpers -------------------------------------------------------------
    def wt(self, *args, cwd=None, check=True):
        return run(["bash", str(SCRIPT), *args], cwd or self.repo,
                   env=self.env, check=check)

    def wtpath(self, branch):
        return self.wtbase / "repo" / branch.replace("/", "-")

    def mkbranch(self, name, fname, msg=None):
        """Cria branch com 1 commit a partir de main e volta para main."""
        git(["checkout", "-qb", name], self.repo)
        (self.repo / fname).write_text(fname + "\n")
        git(["add", "."], self.repo)
        git(["commit", "-qm", msg or f"feat {fname}"], self.repo)
        git(["checkout", "-q", "main"], self.repo)

    def add_origin(self):
        """Origin = bare repo local (sem GitHub: prova pr-merged indisponivel)."""
        bare = self.tmp / "origin.git"
        git(["init", "-q", "--bare", str(bare)], self.tmp)
        git(["remote", "add", "origin", str(bare)], self.repo)
        git(["push", "-qu", "origin", "main"], self.repo)
        return bare

    def branches(self):
        p = git(["for-each-ref", "--format=%(refname:short)", "refs/heads"], self.repo)
        return p.stdout.split()

    def backups(self):
        p = git(["for-each-ref", "--format=%(refname)", "refs/backups"], self.repo)
        return p.stdout.split()

    # -- create / remove: guardas -------------------------------------------
    def test_create_and_audit_ok(self):
        p = self.wt("create", "feat/x")
        self.assertIn("OK  worktree:", p.stdout)
        self.assertTrue(self.wtpath("feat/x").is_dir())
        p = self.wt("audit")
        self.assertIn("OK:", p.stdout)

    def test_remove_refuses_outside_base(self):
        outside = self.tmp / "fora"
        git(["worktree", "add", "-q", str(outside), "-b", "feat/fora"], self.repo)
        p = self.wt("remove", str(outside), check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("RECUSADO", p.stderr)
        self.assertTrue(outside.is_dir())  # nada removido

    def test_remove_refuses_main_worktree(self):
        # worktree principal fora da base ja e recusado pelo under_base;
        # o guard dedicado cobre WT_BASE apontando para dentro do repo.
        p = self.wt("remove", str(self.repo), check=False)
        self.assertNotEqual(p.returncode, 0)

    def test_remove_aborts_on_dirty_tracked(self):
        self.wt("create", "feat/d")
        wt = self.wtpath("feat/d")
        (wt / "a.txt").write_text("mudado\n")
        p = self.wt("remove", str(wt), check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertTrue(wt.is_dir())

    def test_remove_aborts_on_untracked(self):
        """Vetor A medido: untracked (.env, anotacoes) bloqueia sem --force."""
        self.wt("create", "feat/u")
        wt = self.wtpath("feat/u")
        (wt / ".env.local").write_text("segredo\n")
        p = self.wt("remove", str(wt), check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertTrue((wt / ".env.local").is_file())  # nada perdido

    def test_remove_detached_orphan_is_anchored(self):
        """Vetor B medido: git remove worktree detached limpo SEM aviso; o
        commit orfao fica solto e morre no gc. O guard ancora antes."""
        dest = self.wtbase / "repo" / "det"
        dest.parent.mkdir(parents=True, exist_ok=True)
        git(["worktree", "add", "-q", "--detach", str(dest), "main"], self.repo)
        (dest / "x.txt").write_text("x\n")
        git(["add", "."], dest)
        git(["commit", "-qm", "orfao em detached"], dest)
        sha = git(["rev-parse", "HEAD"], dest).stdout.strip()
        p = self.wt("remove", str(dest))
        self.assertIn("ancorado em refs/backups/", p.stdout)
        self.assertFalse(dest.exists())
        anchored = [b for b in self.backups() if "detached-det" in b]
        self.assertEqual(len(anchored), 1)
        got = git(["rev-parse", anchored[0]], self.repo).stdout.strip()
        self.assertEqual(got, sha)  # commit recuperavel

    # -- close: cascata de provas -------------------------------------------
    def test_close_ancestral_proof_full_ceremony(self):
        """Merge ff (ancestral) + origin: worktree, branch local e remota caem
        com prova impressa e ancora criada."""
        self.add_origin()
        self.wt("create", "feat/ok")
        wt = self.wtpath("feat/ok")
        (wt / "b.txt").write_text("b\n")
        git(["add", "."], wt)
        git(["commit", "-qm", "feat b"], wt)
        git(["push", "-qu", "origin", "feat/ok"], wt)
        git(["merge", "-q", "--ff-only", "feat/ok"], self.repo)
        git(["push", "-q", "origin", "main"], self.repo)
        p = self.wt("close", "feat/ok")
        self.assertIn("prova: ancestral", p.stdout)
        self.assertIn("branch remota removida", p.stdout)
        self.assertFalse(wt.exists())
        self.assertNotIn("feat/ok", self.branches())
        self.assertEqual(len([b for b in self.backups() if "feat-ok" in b]), 1)
        ls = git(["ls-remote", "--heads", "origin", "feat/ok"], self.repo)
        self.assertEqual(ls.stdout.strip(), "")  # remota realmente fora

    def test_close_patch_id_proof_remote_rebase(self):
        """Rebase remoto simulado (cherry-pick: mesmo patch, SHA novo).
        `git branch --merged` nao ve; a prova patch-id autoriza."""
        self.mkbranch("feat/reb", "c.txt")
        # main avanca e absorve o patch com SHA diferente
        (self.repo / "z.txt").write_text("z\n")
        git(["add", "."], self.repo)
        git(["commit", "-qm", "main avanca"], self.repo)
        git(["cherry-pick", "feat/reb"], self.repo)
        p = self.wt("close", "feat/reb")
        self.assertIn("prova: patch-id", p.stdout)
        self.assertNotIn("feat/reb", self.branches())

    def test_close_fail_closed_squash_multi(self):
        """Squash de 2 commits: nem ancestral nem patch-id; sem GitHub nao ha
        prova pr-merged -> NADA e removido (fail-closed correto)."""
        git(["checkout", "-qb", "feat/sq"], self.repo)
        for f in ("s1.txt", "s2.txt"):
            (self.repo / f).write_text(f + "\n")
            git(["add", "."], self.repo)
            git(["commit", "-qm", f"feat {f}"], self.repo)
        git(["checkout", "-q", "main"], self.repo)
        git(["merge", "-q", "--squash", "feat/sq"], self.repo)
        git(["commit", "-qm", "feat: squashed"], self.repo)
        p = self.wt("close", "feat/sq", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("SEM PROVA", p.stderr)
        self.assertIn("feat/sq", self.branches())  # preservada
        self.assertEqual(self.backups(), [])       # nada ancorado, nada mexido

    def test_close_refuses_dirty_worktree(self):
        self.wt("create", "feat/suja")
        wt = self.wtpath("feat/suja")
        (wt / "w.txt").write_text("wip\n")
        p = self.wt("close", "feat/suja", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("sujo", p.stderr)
        self.assertTrue(wt.is_dir())

    def test_close_refuses_tip_ahead(self):
        """Commit extra depois do merge: cherry acusa '+' -> preservar."""
        self.mkbranch("feat/ahead", "d.txt")
        git(["merge", "-q", "--ff-only", "feat/ahead"], self.repo)
        git(["checkout", "-q", "feat/ahead"], self.repo)
        (self.repo / "extra.txt").write_text("extra\n")
        git(["add", "."], self.repo)
        git(["commit", "-qm", "trabalho novo pos-merge"], self.repo)
        git(["checkout", "-q", "main"], self.repo)
        p = self.wt("close", "feat/ahead", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("feat/ahead", self.branches())

    def test_close_idempotent(self):
        self.mkbranch("feat/idem", "e.txt")
        git(["merge", "-q", "--ff-only", "feat/idem"], self.repo)
        self.wt("close", "feat/idem")
        p = self.wt("close", "feat/idem")  # segunda vez: rc 0, nada a fazer
        self.assertIn("nada a fazer", p.stdout)

    def test_close_refuses_base_branch(self):
        p = self.wt("close", "main", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("branch base", p.stderr)

    # -- organize ------------------------------------------------------------
    def test_organize_classifies_and_apply_closes_only_proven(self):
        # ABSORVIDA: mergeada em main
        self.mkbranch("feat/absorvida", "f1.txt")
        git(["merge", "-q", "--ff-only", "feat/absorvida"], self.repo)
        # UNICA: commits proprios, nao mergeada
        self.mkbranch("feat/unica", "f2.txt")
        # SUJO: worktree com mudanca
        self.wt("create", "feat/wip")
        (self.wtpath("feat/wip") / "g.txt").write_text("wip\n")

        p = self.wt("organize", check=False)
        self.assertIn("[ABSORVIDA]", p.stdout)
        self.assertIn("[UNICA]", p.stdout)
        self.assertIn("[SUJO]", p.stdout)
        self.assertIn("relatorio apenas", p.stdout)          # fail-closed default
        self.assertIn("feat/absorvida", self.branches())      # relatorio nao age
        self.assertNotEqual(p.returncode, 0)  # audit acusa absorvida viva

        p = self.wt("organize", "--apply", check=False)
        self.assertIn("close concluido: feat/absorvida", p.stdout)
        self.assertNotIn("feat/absorvida", self.branches())   # provada: fechada
        self.assertIn("feat/unica", self.branches())          # unica: preservada
        self.assertTrue(self.wtpath("feat/wip").is_dir())     # sujo: intocado

    def test_organize_deep_finds_lost_stash(self):
        """Regressao do incidente: stash dropado sobrevive como objeto solto;
        --deep aponta o resgate."""
        (self.repo / "a.txt").write_text("stash-me\n")
        git(["stash", "push", "-q", "-m", "wip perdido"], self.repo)
        git(["stash", "drop", "-q"], self.repo)
        p = self.wt("organize", "--deep", check=False)
        self.assertIn("stashes perdidos", p.stdout)
        self.assertIn("git stash apply", p.stdout)

    # -- audit ---------------------------------------------------------------
    def test_audit_flags_absorbed_alive(self):
        self.mkbranch("feat/viva", "h.txt")
        git(["merge", "-q", "--ff-only", "feat/viva"], self.repo)
        p = self.wt("audit", check=False)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("ABSORVIDA-VIVA: feat/viva", p.stdout)
        self.wt("close", "feat/viva")
        p = self.wt("audit")
        self.assertIn("OK:", p.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=1)
