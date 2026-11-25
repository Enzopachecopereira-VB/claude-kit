#!/usr/bin/env bash
# Wrapper fino para o cerimonial da skill git-pro. NAO reimplementa o contrato.
#
# Duas implementacoes do mesmo contrato divergiram em menos de uma hora quando
# existiram em paralelo neste ecossistema. Este arquivo existe so para dar ao
# repo um entrypoint local familiar (`bash scripts/publish-release.sh X.Y.Z`).
#
# Resolucao, em ordem: $GIT_PRO_RELEASE -> copia versionada em scripts/ ->
# instalacao da skill em ~/.agents. Repo que roda CI sem ~/.agents deve
# versionar release.sh + release_engine.py e apontar GIT_PRO_RELEASE.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for candidate in \
  "${GIT_PRO_RELEASE:-}" \
  "$here/release.sh" \
  "$HOME/.agents/skills/git-pro/scripts/release.sh"
do
  [ -n "$candidate" ] && [ -f "$candidate" ] && exec bash "$candidate" publish "$@"
done
printf 'release: cerimonial nao encontrado. Defina GIT_PRO_RELEASE ou instale a skill git-pro.\n' >&2
exit 2
