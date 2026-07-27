#!/usr/bin/env node
// Status line do Claude Code — lê o JSON da sessão via stdin e imprime uma linha colorida.
// Config em settings.json: "statusLine": { "type": "command", "command": "node C:/Users/Epacheco/.claude/statusline.js" }
'use strict';
const { execSync } = require('child_process');

const RESET = '\x1b[0m';
const DIM = '\x1b[2m';
const CYAN = '\x1b[36m';
const MAGENTA = '\x1b[35m';
const GREEN = '\x1b[32m';
const YELLOW = '\x1b[33m';
const RED = '\x1b[31m';

const DIAS = ['dom', 'seg', 'ter', 'qua', 'qui', 'sex', 'sáb'];

// verde < 50%, amarelo 50–79%, vermelho >= 80%
function corPct(p) {
  return p >= 80 ? RED : p >= 50 ? YELLOW : GREEN;
}

function fmtTokens(n) {
  if (n >= 1e6) return (n % 1e6 === 0 ? n / 1e6 : (n / 1e6).toFixed(1)) + 'M';
  if (n >= 1e3) return Math.round(n / 1e3) + 'k';
  return String(n);
}

function hhmm(d) {
  return String(d.getHours()).padStart(2, '0') + 'h' + String(d.getMinutes()).padStart(2, '0');
}

let raw = '';
process.stdin.on('data', (c) => (raw += c));
process.stdin.on('end', () => {
  const parts = [];
  try {
    const d = JSON.parse(raw);

    // Modelo + effort — ex.: "Opus 4.8 (high)"
    if (d.model && d.model.display_name) {
      const eff = d.effort && d.effort.level ? ` (${d.effort.level})` : '';
      parts.push(CYAN + d.model.display_name + eff + RESET);
    }

    // Branch git (omitida se não for repositório)
    try {
      const cwd = (d.workspace && d.workspace.current_dir) || d.cwd;
      if (cwd) {
        const br = execSync('git branch --show-current', {
          cwd,
          timeout: 1500,
          stdio: ['ignore', 'pipe', 'ignore'],
        })
          .toString()
          .trim();
        if (br) parts.push(MAGENTA + br + RESET);
      }
    } catch (_) {}

    // Contexto da sessão — ex.: "ctx 12% (24k/200k)"
    const cw = d.context_window;
    if (cw && cw.context_window_size) {
      const usados = cw.total_input_tokens || 0;
      const pct =
        cw.used_percentage != null
          ? Math.round(cw.used_percentage)
          : Math.round((usados / cw.context_window_size) * 100);
      parts.push(
        corPct(pct) + `ctx ${pct}% (${fmtTokens(usados)}/${fmtTokens(cw.context_window_size)})` + RESET
      );
    }

    // Janela de 5 horas — ex.: "5h: 34% ↻ 21h15"
    const rl = d.rate_limits;
    if (rl && rl.five_hour && rl.five_hour.used_percentage != null) {
      const p = Math.round(rl.five_hour.used_percentage);
      let s = `5h: ${p}%`;
      if (rl.five_hour.resets_at) s += ` ↻ ${hhmm(new Date(rl.five_hour.resets_at * 1000))}`;
      parts.push(corPct(p) + s + RESET);
    }

    // Janela semanal — ex.: "sem: 41% ↻ qui 09h00"
    if (rl && rl.seven_day && rl.seven_day.used_percentage != null) {
      const p = Math.round(rl.seven_day.used_percentage);
      let s = `sem: ${p}%`;
      if (rl.seven_day.resets_at) {
        const dt = new Date(rl.seven_day.resets_at * 1000);
        s += ` ↻ ${DIAS[dt.getDay()]} ${hhmm(dt)}`;
      }
      parts.push(corPct(p) + s + RESET);
    }
  } catch (_) {
    // JSON inválido ou erro inesperado: não quebra a status line
  }
  process.stdout.write(parts.join(DIM + ' | ' + RESET));
});
