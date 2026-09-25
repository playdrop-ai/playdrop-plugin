import assert from "node:assert/strict";
import { readFileSync, readdirSync, lstatSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const read = (root, file) => JSON.parse(readFileSync(path.join(root, file), "utf8"));
const equalKeys = (value, keys) => assert.deepEqual(Object.keys(value).sort(), keys.sort());
const shared = ["LICENSE", "skills/playdrop-ai/SKILL.md",
  "assets/playdrop-icon-small.svg", "assets/playdrop-icon-large.png"];
const prefixes = {
  "": ["plugin.json", "mcp.json"],
  "plugins/playdrop/": [".codex-plugin/plugin.json", ".mcp.json", "README.md"],
  "variants/claude/playdrop/": [".claude-plugin/plugin.json", ".mcp.json", "README.md"],
  "variants/antigravity/playdrop/": ["plugin.json", "mcp_config.json", "README.md"],
  "variants/grok/playdrop/": ["plugin.json", ".grok-plugin/plugin.json", ".mcp.json", "README.md"],
};
export function files(root, prefix = "") {
  return readdirSync(path.join(root, prefix)).filter((name) => prefix || name !== ".git").sort().flatMap((name) => {
    const relative = prefix + name;
    const stat = lstatSync(path.join(root, relative));
    assert(!stat.isSymbolicLink(), `Symlinks are not allowed: ${relative}`);
    if (stat.isDirectory()) return files(root, relative + "/");
    assert(stat.isFile(), `Not a regular file: ${relative}`);
    return [relative];
  });
}
export function validatePackage(root) {
  const expected = ["README.md", "INSTALLATION.md", "SECURITY.md", "CHANGELOG.md", "CODE_OF_CONDUCT.md",
    "server.json", "gemini-extension.json", ".github/CODEOWNERS", ".github/CONTRIBUTING.md", ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml", ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/config.yml", "tools/validate-package.mjs",
    ".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json", ".grok-plugin/marketplace.json"];
  for (const [prefix, specific] of Object.entries(prefixes)) {
    expected.push(...[...shared, ...specific].map((file) => prefix + file));
  }
  assert.deepEqual(files(root).sort(), expected.sort(), "Unexpected or missing public package files");
  const manifest = read(root, "plugin.json");
  equalKeys(manifest, ["$schema", "name", "version", "description", "author", "homepage",
    "repository", "license", "keywords"]);
  assert.equal(manifest.$schema, "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json");
  assert.equal(manifest.name, "playdrop");
  assert.match(manifest.version, /^\d+\.\d+\.\d+$/);
  assert.equal(manifest.license, "MIT");
  assert.equal(manifest.repository, "https://github.com/playdrop-ai/playdrop-plugin");
  const portable = read(root, "mcp.json");
  equalKeys(portable, ["$schema", "mcpServers"]);
  assert.equal(portable.$schema, "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json");
  equalKeys(portable.mcpServers, ["playdrop"]);
  equalKeys(portable.mcpServers.playdrop, ["type", "url"]);
  assert.equal(portable.mcpServers.playdrop.type, "streamable-http");
  const url = portable.mcpServers.playdrop.url;
  const parsed = new URL(url);
  assert(parsed.protocol === "https:" && parsed.pathname === "/mcp" && !parsed.username &&
    !parsed.password && !parsed.search && !parsed.hash, "Unsafe endpoint URL");
  const native = [
    ["plugins/playdrop/.mcp.json", { type: "http", url,
      oauth: { clientId: "playdrop-codex", callbackUrl: "http://127.0.0.1/callback" } }],
    ["variants/claude/playdrop/.mcp.json", { type: "http", url, oauth: { clientId: "playdrop-claude-code" } }],
    ["variants/antigravity/playdrop/mcp_config.json", { serverUrl: url }],
    ["variants/grok/playdrop/.mcp.json", { type: "http", url }],
  ];
  for (const [file, server] of native) assert.deepEqual(read(root, file), { mcpServers: { playdrop: server } });
  const codex = read(root, "plugins/playdrop/.codex-plugin/plugin.json");
  assert.equal(codex.name, manifest.name);
  assert.equal(codex.version, manifest.version);
  assert.equal(codex.mcpServers, "./.mcp.json");
  assert.equal(codex.skills, "./skills/");
  assert.deepEqual(read(root, "variants/claude/playdrop/.claude-plugin/plugin.json"),
    Object.fromEntries(Object.entries(manifest).filter(([key]) => key !== "$schema")));
  for (const file of ["plugin.json", ".grok-plugin/plugin.json"]) {
    assert.deepEqual(read(root, `variants/grok/playdrop/${file}`),
      Object.fromEntries(Object.entries(manifest).filter(([key]) => key !== "$schema")));
  }
  assert.deepEqual(read(root, "variants/antigravity/playdrop/plugin.json"), {
    $schema: "https://antigravity.google/schemas/v1/plugin.json",
    name: manifest.name, description: manifest.description,
  });
  for (const prefix of Object.keys(prefixes)) {
    for (const file of shared) assert.deepEqual(readFileSync(path.join(root, prefix, file)),
      readFileSync(path.join(root, file)), `Shared component differs: ${prefix}${file}`);
  }
  assert.match(readFileSync(path.join(root, "LICENSE"), "utf8"), /Copyright \(c\) 2026 PlayDrop Inc\./);
  const skill = readFileSync(path.join(root, "skills/playdrop-ai/SKILL.md"), "utf8");
  assert.match(skill, /^---\nname: playdrop-ai\ndescription: .+\n---\n/);
  assert.deepEqual(read(root, ".agents/plugins/marketplace.json").plugins[0].source,
    { source: "local", path: "./plugins/playdrop" });
  assert.equal(read(root, ".claude-plugin/marketplace.json").plugins[0].source, "./variants/claude/playdrop");
  assert.deepEqual(read(root, ".grok-plugin/marketplace.json").plugins[0].source,
    { type: "local", path: "./variants/grok/playdrop" });
  assert.deepEqual(read(root, "gemini-extension.json"), { name: manifest.name, version: manifest.version,
    description: manifest.description, mcpServers: { playdrop: { httpUrl: url } } });
  const registry = read(root, "server.json");
  assert.equal(registry.name, "ai.playdrop/mcp");
  assert.equal(registry.version, manifest.version);
  assert(registry.description.length <= 100, "Registry description exceeds 100 characters");
  assert.deepEqual(registry.remotes, [{ type: "streamable-http", url }]);
  return { version: manifest.version, endpoint: url, files: expected.length };
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const root = path.resolve(process.argv[2] ?? path.join(path.dirname(fileURLToPath(import.meta.url)), ".."));
  console.log(JSON.stringify(validatePackage(root), null, 2));
}
