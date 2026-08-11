#!/usr/bin/env node
/**
 * Lightweight static check for .cursor/mcp.json (no secrets printed).
 */

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const DEFAULT_MCP_PATH = path.join(ROOT, ".cursor", "mcp.json");

const SUPPORTED_SERVERS = [
  "chrome-devtools",
  "context7",
  "filesystem",
  "github",
  "playwright",
];

const DANGEROUS_PATH_PATTERNS = [
  /^\/$/,
  /^[A-Za-z]:\\?$/,
  /^~\/ ?$/,
  /^\/Users\/[^/]+\/?$/,
  /^\/home\/[^/]+\/?$/,
  /^C:\\Users\\[^\\]+\/?$/i,
  /^\/Volumes\/?$/,
];

const SENSITIVE_ENV_KEY = /(token|secret|password|api[_-]?key|cookie|session)/i;

function isDangerousPath(arg) {
  const normalized = String(arg).trim().replace(/\\/g, "/");
  if (["/", "//", "C:", "C:/"].includes(normalized)) return true;
  return DANGEROUS_PATH_PATTERNS.some((pat) => pat.test(normalized));
}

function looksLikeLiteralSecret(value) {
  const s = String(value);
  if (!s || s.startsWith("${")) return false;
  if (s.startsWith("ghp_") || s.startsWith("github_pat_")) return true;
  if (s.length >= 20 && /[a-zA-Z0-9]{20,}/.test(s)) {
    if (!s.includes("env:") && !s.includes("GITHUB_TOKEN")) return true;
  }
  return false;
}

function collectPathArgs(server) {
  const args = server.args;
  if (!Array.isArray(args)) return [];
  return args.filter((a) => typeof a === "string" || typeof a === "number");
}

function summarizeServer(name, cfg) {
  const hasCommand = typeof cfg.command === "string" && cfg.command.length > 0;
  const argCount = Array.isArray(cfg.args) ? cfg.args.length : 0;
  const envKeyCount =
    cfg.env && typeof cfg.env === "object"
      ? Object.keys(cfg.env).length
      : 0;
  return `  - ${name}: command_configured=${hasCommand} arg_count=${argCount} env_key_count=${envKeyCount}`;
}

function main() {
  const configIndex = process.argv.indexOf("--config");
  const configArg = configIndex >= 0 ? process.argv[configIndex + 1] : null;
  if (configIndex >= 0 && !configArg) {
    console.error("ERROR: --config requires a path");
    process.exit(1);
  }
  const mcpPath = configArg ? path.resolve(configArg) : DEFAULT_MCP_PATH;
  console.log("MCP config: selected");

  if (!fs.existsSync(mcpPath)) {
    console.error("ERROR: .cursor/mcp.json not found");
    process.exit(1);
  }

  let data;
  try {
    data = JSON.parse(fs.readFileSync(mcpPath, "utf8"));
  } catch (err) {
    console.error(`ERROR: invalid JSON: ${err.message}`);
    process.exit(1);
  }

  const servers = data.mcpServers;
  if (!servers || typeof servers !== "object" || Array.isArray(servers)) {
    console.error("ERROR: mcpServers must be an object");
    process.exit(1);
  }

  const names = Object.keys(servers).sort();
  console.log(`Servers (${names.length}): ${names.join(", ") || "(none)"}`);
  console.log("Summary:");
  for (const name of names) {
    const cfg = servers[name];
    if (cfg && typeof cfg === "object") {
      console.log(summarizeServer(name, cfg));
    }
  }

  const errors = [];
  const warnings = [];

  for (const [name, cfg] of Object.entries(servers)) {
    if (!cfg || typeof cfg !== "object") {
      errors.push(`${name}: config must be an object`);
      continue;
    }

    const isFilesystem =
      name === "filesystem" ||
      (Array.isArray(cfg.args) &&
        cfg.args.some((a) => String(a).includes("filesystem")));

    if (isFilesystem) {
      for (const arg of collectPathArgs(cfg)) {
        if (isDangerousPath(arg)) {
          errors.push(
            "filesystem: dangerous allowed path configured (use project workspace only)"
          );
        } else if (String(arg) === ".") {
          warnings.push(
            "filesystem: uses '.' — OK if Cursor cwd is repo root; else set single-repo absolute path locally"
          );
        }
      }
    }

    if (cfg.env && typeof cfg.env === "object") {
      for (const [key, val] of Object.entries(cfg.env)) {
        if (SENSITIVE_ENV_KEY.test(String(key)) && looksLikeLiteralSecret(val)) {
          errors.push(`${name}: env '${key}' looks like a hardcoded secret`);
        }
        if (
          String(val).startsWith("ghp_") ||
          String(val).startsWith("github_pat_")
        ) {
          errors.push(`${name}: GitHub token must not be committed`);
        }
      }
    }
  }

  if (names.includes("github")) {
    const gh = servers.github || {};
    const env = gh.env && typeof gh.env === "object" ? gh.env : {};
    const tokenRef = String(env.GITHUB_PERSONAL_ACCESS_TOKEN || "");
    if (!tokenRef.startsWith("${")) {
      warnings.push(
        "github: use env var reference (e.g. ${env:GITHUB_TOKEN}); set token in shell/Cursor env, never commit"
      );
    }
  }

  for (const w of warnings) console.log(`WARN: ${w}`);
  for (const e of errors) console.error(`ERROR: ${e}`);

  if (errors.length > 0) process.exit(1);

  console.log("OK: MCP config static check passed");
  console.log(
    `Supported candidates (not runtime claims): ${SUPPORTED_SERVERS.join(", ")}`
  );
  process.exit(0);
}

main();
