#!/usr/bin/env node
/**
 * audit_bi_tokens.mjs
 *
 * Varredura estática (zero deps) para violações do padrão bi-frontends:
 *   - gradiente em background
 *   - backdrop-filter: blur em superfície de dado
 *   - box-shadow colorido em card estático
 *   - hex hardcoded fora de arquivo de token
 *   - border-radius acima de 16px
 *   - falta de tabular-nums em classe .kpi/.table-cell/numeric
 *   - mais de 7 cores hex distintas num mesmo arquivo de tema
 *   - import misto de mais de uma lib de ícone no mesmo projeto
 *
 * Uso:
 *   node audit_bi_tokens.mjs <dir>
 *
 * Exit code 0 = sem violações. Exit code 1 = violações encontradas (gate de CI).
 */

import { readdirSync, readFileSync, statSync } from "node:fs";
import { extname, join, relative } from "node:path";

const targetDir = process.argv[2] ?? "src";
const CSS_EXTS = new Set([".css", ".scss", ".less"]);
const CODE_EXTS = new Set([".css", ".scss", ".less", ".tsx", ".ts", ".jsx", ".js"]);
const TOKEN_FILE_HINT = /(tokens?|theme|design-system)/i;
const ICON_LIBS = [
  { name: "lucide-react", pattern: /from\s+["']lucide-react["']/ },
  { name: "@tabler/icons-react", pattern: /from\s+["']@tabler\/icons-react["']/ },
  { name: "@phosphor-icons/react", pattern: /from\s+["']@phosphor-icons\/react["']/ },
  { name: "@carbon/icons-react", pattern: /from\s+["']@carbon\/icons-react["']/ },
  { name: "react-icons", pattern: /from\s+["']react-icons/ },
];

const IGNORE_DIRS = new Set(["node_modules", ".next", "dist", "build", ".git", ".turbo"]);

/** @type {{file: string, rule: string, detail: string}[]} */
const violations = [];
const iconLibsFound = new Map(); // lib name -> Set<file>
const hexColorsByFile = new Map(); // file -> Set<hex>

function walk(dir) {
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    if (IGNORE_DIRS.has(entry.name)) continue;
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full);
    } else if (entry.isFile()) {
      const ext = extname(entry.name);
      if (CODE_EXTS.has(ext)) checkFile(full, ext);
    }
  }
}

function checkFile(filePath, ext) {
  let content;
  try {
    content = readFileSync(filePath, "utf8");
  } catch {
    return;
  }
  const rel = relative(process.cwd(), filePath);
  const isTokenFile = TOKEN_FILE_HINT.test(filePath);

  // 1. gradiente em background
  const gradientBgMatches = content.match(/background(?:-image)?\s*:\s*(?:linear|radial|conic)-gradient/gi);
  if (gradientBgMatches) {
    violations.push({
      file: rel,
      rule: "no-gradient-background",
      detail: `${gradientBgMatches.length} ocorrência(s) de gradient em background`,
    });
  }

  // 2. backdrop-filter blur (glassmorphism)
  if (/backdrop-filter\s*:\s*blur/i.test(content)) {
    violations.push({
      file: rel,
      rule: "no-glassmorphism",
      detail: "backdrop-filter: blur() encontrado — glassmorphism fora de escopo em superfície de dado",
    });
  }

  // 3. box-shadow colorido (heurística: box-shadow com rgb/rgba não-cinza ou hex, fora de .overlay/.dropdown/.modal/.popover)
  const shadowMatches = [...content.matchAll(/box-shadow\s*:\s*[^;]+;/gi)];
  for (const m of shadowMatches) {
    const decl = m[0];
    const looksColored = /rgba?\([^)]*\)/i.test(decl) && !/rgba?\(0,\s*0,\s*0/i.test(decl);
    const nearOverlayContext = /(overlay|dropdown|modal|popover|tooltip)/i.test(
      content.slice(Math.max(0, m.index - 200), m.index)
    );
    if (looksColored && !nearOverlayContext) {
      violations.push({
        file: rel,
        rule: "no-colored-shadow-on-static-card",
        detail: `box-shadow potencialmente colorido fora de contexto de overlay: "${decl.trim()}"`,
      });
    }
  }

  // 4. border-radius acima de 16px
  const radiusMatches = [...content.matchAll(/border-radius\s*:\s*(\d+(?:\.\d+)?)px/gi)];
  for (const m of radiusMatches) {
    const value = parseFloat(m[1]);
    if (value > 16) {
      violations.push({
        file: rel,
        rule: "border-radius-over-limit",
        detail: `border-radius: ${value}px (teto recomendado: 12px, máximo tolerado: 16px)`,
      });
    }
  }

  // 5. hex hardcoded fora de arquivo de token
  if (CSS_EXTS.has(ext) && !isTokenFile) {
    const hexMatches = content.match(/#[0-9a-fA-F]{3,8}\b/g);
    if (hexMatches && hexMatches.length > 0) {
      violations.push({
        file: rel,
        rule: "hardcoded-hex-outside-tokens",
        detail: `${hexMatches.length} valor(es) hex fora de arquivo de token: ${[...new Set(hexMatches)].slice(0, 5).join(", ")}${hexMatches.length > 5 ? "..." : ""}`,
      });
    }
  }

  // 6. contagem de cores por arquivo de tema (mais de 7 cores categóricas)
  if (isTokenFile) {
    const hexMatches = content.match(/#[0-9a-fA-F]{6}\b/g) ?? [];
    hexColorsByFile.set(rel, new Set(hexMatches));
  }

  // 7. classes .kpi / .table-cell--numeric sem tabular-nums na proximidade (heurística por bloco CSS)
  if (CSS_EXTS.has(ext)) {
    const ruleBlocks = content.match(/\.[\w-]*(?:kpi-value|table-cell--numeric|kpi-delta)[^{]*\{[^}]*\}/gi) ?? [];
    for (const block of ruleBlocks) {
      if (!/tabular-nums/i.test(block)) {
        violations.push({
          file: rel,
          rule: "missing-tabular-nums",
          detail: `Seletor numérico sem font-variant-numeric: tabular-nums — "${block.split("{")[0].trim()}"`,
        });
      }
    }
  }

  // 8. import de lib de ícone
  for (const lib of ICON_LIBS) {
    if (lib.pattern.test(content)) {
      if (!iconLibsFound.has(lib.name)) iconLibsFound.set(lib.name, new Set());
      iconLibsFound.get(lib.name).add(rel);
    }
  }
}

walk(targetDir);

// pós-processamento: mais de 7 cores num arquivo de tema
for (const [file, colors] of hexColorsByFile) {
  if (colors.size > 7) {
    violations.push({
      file,
      rule: "too-many-categorical-colors",
      detail: `${colors.size} cores hex distintas no arquivo de tema (máximo recomendado: 7 visíveis simultâneas)`,
    });
  }
}

// pós-processamento: mais de uma lib de ícone no projeto
if (iconLibsFound.size > 1) {
  const summary = [...iconLibsFound.entries()]
    .map(([lib, files]) => `${lib} (${files.size} arquivo(s))`)
    .join(", ");
  violations.push({
    file: targetDir,
    rule: "mixed-icon-libraries",
    detail: `Mais de uma biblioteca de ícone em uso: ${summary} — escolher uma só (ver references/iconography.md)`,
  });
}

// relatório
if (violations.length === 0) {
  console.log("✅ bi-frontends audit: nenhuma violação encontrada.");
  process.exit(0);
}

console.log(`❌ bi-frontends audit: ${violations.length} violação(ões) encontrada(s):\n`);
const byRule = new Map();
for (const v of violations) {
  if (!byRule.has(v.rule)) byRule.set(v.rule, []);
  byRule.get(v.rule).push(v);
}
for (const [rule, items] of byRule) {
  console.log(`\n[${rule}] (${items.length})`);
  for (const item of items.slice(0, 20)) {
    console.log(`  ${item.file} — ${item.detail}`);
  }
  if (items.length > 20) console.log(`  ... e mais ${items.length - 20}`);
}

process.exit(1);
