#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const defaultRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const pluginRoot = path.resolve(process.argv[2] || defaultRoot);
const manifestPath = path.join(pluginRoot, "plugin.json");
const schemaUrl = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json";
const allowedManifestFields = new Set([
  "$schema",
  "name",
  "version",
  "description",
  "author",
  "homepage",
  "repository",
  "license",
  "keywords",
  "extensions",
]);
const allowedAuthorFields = new Set(["name", "email", "url"]);
const pluginNamePattern = /^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$/;
const semverPattern = /^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$/;
const skillNamePattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

function fail(code, detail = "") {
  throw new Error(`${code}${detail ? `:${detail}` : ""}`);
}

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
  } catch (error) {
    fail("plugin_validation_invalid_json", `${path.relative(pluginRoot, filePath)}:${error.message}`);
  }
}

function requireString(value, label) {
  if (typeof value !== "string" || !value.trim()) fail("plugin_validation_missing_string", label);
}

function parseFrontmatter(contents, relativePath) {
  const match = contents.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  if (!match) fail("plugin_validation_skill_frontmatter_missing", relativePath);
  const values = {};
  for (const line of match[1].split(/\r?\n/)) {
    const field = line.match(/^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$/);
    if (!field) continue;
    values[field[1]] = field[2].trim().replace(/^(["'])(.*)\1$/, "$2");
  }
  return values;
}

function validateManifest() {
  if (!fs.statSync(manifestPath, { throwIfNoEntry: false })?.isFile()) {
    fail("plugin_validation_manifest_missing", "plugin.json");
  }
  const manifest = readJson(manifestPath);
  if (!manifest || typeof manifest !== "object" || Array.isArray(manifest)) {
    fail("plugin_validation_manifest_not_object");
  }
  for (const field of Object.keys(manifest)) {
    if (!allowedManifestFields.has(field)) fail("plugin_validation_unknown_manifest_field", field);
  }
  if (manifest.$schema !== schemaUrl) fail("plugin_validation_schema_mismatch", String(manifest.$schema || "missing"));
  requireString(manifest.name, "name");
  if (manifest.name.length > 64 || !pluginNamePattern.test(manifest.name)) {
    fail("plugin_validation_invalid_name", manifest.name);
  }
  requireString(manifest.version, "version");
  if (!semverPattern.test(manifest.version)) fail("plugin_validation_invalid_version", manifest.version);
  requireString(manifest.description, "description");
  requireString(manifest.homepage, "homepage");
  requireString(manifest.repository, "repository");
  requireString(manifest.license, "license");
  if (!manifest.author || typeof manifest.author !== "object" || Array.isArray(manifest.author)) {
    fail("plugin_validation_invalid_author");
  }
  for (const field of Object.keys(manifest.author)) {
    if (!allowedAuthorFields.has(field)) fail("plugin_validation_unknown_author_field", field);
  }
  requireString(manifest.author.name, "author.name");
  if (
    !Array.isArray(manifest.keywords) ||
    manifest.keywords.some((entry) => typeof entry !== "string" || !entry.trim())
  ) {
    fail("plugin_validation_invalid_keywords");
  }
  return manifest;
}

function validateSkills() {
  const skillsRoot = path.join(pluginRoot, "skills");
  if (!fs.statSync(skillsRoot, { throwIfNoEntry: false })?.isDirectory()) {
    fail("plugin_validation_skills_missing");
  }
  const skillDirectories = fs
    .readdirSync(skillsRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .sort((left, right) => left.name.localeCompare(right.name));
  if (skillDirectories.length === 0) fail("plugin_validation_skills_empty");
  for (const entry of skillDirectories) {
    const relativePath = `skills/${entry.name}/SKILL.md`;
    const skillPath = path.join(pluginRoot, relativePath);
    if (!fs.statSync(skillPath, { throwIfNoEntry: false })?.isFile()) {
      fail("plugin_validation_skill_file_missing", relativePath);
    }
    const contents = fs.readFileSync(skillPath, "utf8");
    const frontmatter = parseFrontmatter(contents, relativePath);
    if (frontmatter.name !== entry.name || !skillNamePattern.test(frontmatter.name || "")) {
      fail("plugin_validation_skill_name_mismatch", `${relativePath}:${frontmatter.name || "missing"}`);
    }
    requireString(frontmatter.description, `${relativePath}:description`);
    if (frontmatter.description.length < 40) fail("plugin_validation_skill_description_too_short", relativePath);
    const lineCount = contents.split(/\r?\n/).length;
    if (lineCount > 500) fail("plugin_validation_skill_too_long", `${relativePath}:${lineCount}`);
  }
  return skillDirectories.length;
}

function validateLegacyManifestsAbsent() {
  for (const relativePath of [".codex-plugin/plugin.json", ".cursor-plugin/plugin.json"]) {
    if (fs.existsSync(path.join(pluginRoot, relativePath))) {
      fail("plugin_validation_superseded_manifest_present", relativePath);
    }
  }
}

try {
  const manifest = validateManifest();
  validateLegacyManifestsAbsent();
  const skillCount = validateSkills();
  process.stdout.write(`plugin_valid:${manifest.name}:${manifest.version}:skills=${skillCount}\n`);
} catch (error) {
  process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
  process.exitCode = 1;
}
