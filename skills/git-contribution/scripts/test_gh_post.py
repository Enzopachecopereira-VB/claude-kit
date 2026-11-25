#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# --- How to run ---
# python3 skills/git-contribution/scripts/test_gh_post.py -v

from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("gh-post.sh")


def _fixture(kind: str) -> str:
    """Monta o segredo de teste por CONCATENACAO em runtime.

    O literal nunca existe no fonte: o gate anti-segredo do proprio repositorio
    varre todo arquivo rastreado, e um fixture literal faria este teste ser
    acusado como vazamento real. Allowlistar seria a correcao errada: enfraquece
    o gate para acomodar o teste.
    """
    parts = {
        "github": "gh" + "p_" + "1234567890abcdef1234567890abcdef123456",
        "slack": "xo" + "xb-" + "1234567890-abcdefghi",
        "aws": "AK" + "IA" + "1234567890ABCDEF",
        "anthropic": "sk-" + "ant-" + "api03-abcdefghijklmnopqrstuvwxyz",
        "stripe": "sk_" + "live_" + "abcdefghijklmnopqrstuvwxyz",
        "bearer": "Bea" + "rer " + "abcdefghijklmnopqrstuvwxyz123456",
        "pem": "-----BE" + "GIN OPENSSH PRIVATE KEY-----",
        "jwt": ("ey" + "JhbGciOiJIUzI1NiJ9." + "ey" + "JzdWIiOiIxMjM0NTY3ODkwIn0"
                + ".signaturepart123"),
    }
    return parts[kind]


class GhPostSanitizerTest(unittest.TestCase):
    def run_check(
        self,
        text: str,
        *,
        extra_terms: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        if extra_terms is None:
            env.pop("GH_POST_DENY_EXTRA", None)
        else:
            env["GH_POST_DENY_EXTRA"] = extra_terms

        return subprocess.run(
            ["/bin/bash", str(SCRIPT), "--check-only", "-"],
            input=text,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )

    def assert_dirty(self, text: str, class_name: str, *, extra_terms: str | None = None) -> None:
        result = self.run_check(text, extra_terms=extra_terms)
        output = result.stdout + result.stderr
        self.assertNotEqual(
            result.returncode,
            0,
            f"{class_name}: expected sanitizer to exit non-zero for dirty input. Output:\n{output}",
        )
        self.assertIn(
            class_name,
            output,
            f"{class_name}: expected sanitizer output to name offending class. Output:\n{output}",
        )

    def assert_clean(self, text: str) -> None:
        result = self.run_check(text)
        output = result.stdout + result.stderr
        self.assertEqual(
            result.returncode,
            0,
            f"expected sanitizer to accept clean input. Output:\n{output}",
        )

    def test_rejects_posix_absolute_home_path(self) -> None:
        self.assert_dirty("Log lives at /Users/alice/project/output.log\n", "posix-home-path")
        self.assert_dirty("Cache lives at /home/alice/project/output.log\n", "posix-home-path")

    def test_rejects_home_shorthand_path(self) -> None:
        self.assert_dirty("Read ~/project/output.log before replying.\n", "home-shorthand")
        self.assert_dirty("Read $HOME/project/output.log before replying.\n", "home-shorthand")

    def test_rejects_windows_home_path(self) -> None:
        self.assert_dirty("Trace came from C:\\Users\\alice\\project\\log.txt\n", "windows-home-path")

    def test_rejects_hostname(self) -> None:
        self.assert_dirty("Reproduced on Machine.local with the same config.\n", "hostname")
        self.assert_dirty("hostname: build-agent-17\n", "hostname")

    def test_rejects_email_address(self) -> None:
        self.assert_dirty("Contact me at dev@example.com for the logs.\n", "email")

    def test_rejects_github_token(self) -> None:
        self.assert_dirty("Token: " + _fixture("github") + "\n", "github-token")
        self.assert_dirty("Token: " + "gho" + "_" + "1234567890abcdef1234567890abcdef123456" + "\n", "github-token")
        self.assert_dirty("Token: " + "ghu" + "_" + "1234567890abcdef1234567890abcdef123456" + "\n", "github-token")
        self.assert_dirty("Token: " + "ghs" + "_" + "1234567890abcdef1234567890abcdef123456" + "\n", "github-token")
        self.assert_dirty("Token: " + "ghr" + "_" + "1234567890abcdef1234567890abcdef123456" + "\n", "github-token")

    def test_rejects_slack_token(self) -> None:
        self.assert_dirty("Slack token " + _fixture("slack") + " leaked.\n", "slack-token")

    def test_rejects_aws_access_key_id(self) -> None:
        self.assert_dirty("AWS key " + _fixture("aws") + " appeared in env.\n", "aws-access-key-id")

    def test_rejects_anthropic_key(self) -> None:
        self.assert_dirty("Anthropic key " + _fixture("anthropic") + " leaked.\n", "anthropic-key")

    def test_rejects_stripe_live_key(self) -> None:
        self.assert_dirty("Stripe key " + _fixture("stripe") + " leaked.\n", "stripe-live-key")

    def test_rejects_generic_bearer_token(self) -> None:
        self.assert_dirty("Authorization: " + _fixture("bearer") + "\n", "bearer-token")

    def test_rejects_jwt(self) -> None:
        self.assert_dirty(
            "JWT " + _fixture("jwt") + "\n",
            "jwt",
        )

    def test_rejects_private_key_pem_header(self) -> None:
        self.assert_dirty(_fixture("pem") + "\n", "private-key-pem")

    def test_rejects_session_id(self) -> None:
        self.assert_dirty("Session ses_123abc456def was in the log.\n", "session-id")

    def test_rejects_absolute_timestamp(self) -> None:
        self.assert_dirty("Captured at 2026-07-24 18:43:12 on the workstation.\n", "absolute-timestamp")

    def test_rejects_caller_supplied_internal_name(self) -> None:
        self.assert_dirty(
            "The trace references project-codename-redkite.\n",
            "extra-deny-term",
            extra_terms="project-codename-redkite\nrepo-secret-name",
        )

    def test_accepts_normal_technical_paragraph_with_relative_paths(self) -> None:
        self.assert_clean(
            "The failing fixture is under skills/git-contribution/scripts. "
            "Run ./scripts/check.sh from the repo root and attach the relative log path.\n"
        )

    def test_accepts_version_string(self) -> None:
        self.assert_clean("The regression started after version 1.2.3.\n")

    def test_accepts_iso_date_without_time(self) -> None:
        # Dates alone do not localize a machine; only date+time is denied by this gate.
        self.assert_clean("The report was prepared on 2026-07-24.\n")

    def test_accepts_public_placeholders(self) -> None:
        self.assert_clean("Use $PARENT/<repo>/logs/output.txt in the public issue.\n")


if __name__ == "__main__":
    unittest.main()
