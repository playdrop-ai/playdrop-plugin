#!/usr/bin/env node
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const OPENAI_CATEGORIES = new Set([
  "Productivity",
  "Creativity",
  "Developer Tools",
  "Business & Operations",
  "Data & Analytics",
  "Communication",
  "Education & Research",
  "Security",
  "Finance",
  "Healthcare",
  "Travel",
  "Entertainment",
  "Other",
]);
const PNG_SIGNATURE = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
const MAX_ARCHIVE_BYTES = 100 * 1024 * 1024;
const MAX_UNCOMPRESSED_BYTES = 512 * 1024 * 1024;
const MAX_ARCHIVE_ENTRIES = 5000;
const INTERNAL_PATH_PREFIXES = [
  "agent-bundle.json",
  "worker/",
  "skills/task-worker/",
  "skills/review-game/",
  "skills/game-eval/",
  "references/game-review-",
];
const INTERNAL_TEXT_MARKERS = [
  "plugins/playdrop-platform",
  "skills/task-worker",
  "skills/review-game",
  "skills/game-eval",
  "references/game-review-",
  "playdrop-platform:",
];

function fail(code, detail = "") {
  throw new Error(`${code}${detail ? `:${detail}` : ""}`);
}

function readJson(root, relativePath) {
  const absolutePath = path.join(root, relativePath);
  try {
    return JSON.parse(fs.readFileSync(absolutePath, "utf8"));
  } catch (error) {
    fail("submission_invalid_json", `${relativePath}:${error.message}`);
  }
}

function requireObject(value, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    fail("submission_object_required", label);
  }
}

function requireText(value, label, options = {}) {
  if (typeof value !== "string" || !value.trim()) fail("submission_text_required", label);
  if (options.oneLine && /[\r\n]/.test(value)) fail("submission_text_must_be_one_line", label);
  if (options.max && value.length > options.max) {
    fail("submission_text_too_long", `${label}:${value.length}>${options.max}`);
  }
  if (/\p{Cc}|\u2028|\u2029/gu.test(value)) fail("submission_text_unsupported", label);
}

function requireHttpsUrl(value, label, max = 1024) {
  requireText(value, label, { oneLine: true, max });
  let parsed;
  try {
    parsed = new URL(value);
  } catch {
    fail("submission_url_invalid", label);
  }
  if (parsed.protocol !== "https:" || !parsed.hostname || parsed.username || parsed.password) {
    fail("submission_url_invalid", label);
  }
}

function requireStringList(value, label, options = {}) {
  if (!Array.isArray(value)) fail("submission_list_required", label);
  if (options.exact !== undefined && value.length !== options.exact) {
    fail("submission_list_wrong_size", `${label}:${value.length}!=${options.exact}`);
  }
  if (options.max !== undefined && value.length > options.max) {
    fail("submission_list_too_large", `${label}:${value.length}>${options.max}`);
  }
  value.forEach((entry, index) =>
    requireText(entry, `${label}[${index}]`, {
      oneLine: options.oneLine,
      max: options.entryMax,
    }),
  );
}

function relativeLuminance(hex) {
  const channels = [1, 3, 5].map((offset) => Number.parseInt(hex.slice(offset, offset + 2), 16) / 255);
  return channels
    .map((channel) => (channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4))
    .reduce((total, channel, index) => total + channel * [0.2126, 0.7152, 0.0722][index], 0);
}

function contrast(left, right) {
  const brighter = Math.max(relativeLuminance(left), relativeLuminance(right));
  const darker = Math.min(relativeLuminance(left), relativeLuminance(right));
  return (brighter + 0.05) / (darker + 0.05);
}

function validateColor(value, label, background) {
  if (typeof value !== "string" || !/^#[0-9A-Fa-f]{6}$/.test(value)) {
    fail("submission_color_invalid", label);
  }
  if (contrast(value, background) < 2) fail("submission_color_contrast_too_low", label);
}

function validatePng(root, relativePath, label) {
  requireText(relativePath, label, { oneLine: true });
  if (path.isAbsolute(relativePath) || relativePath.split("/").includes("..")) {
    fail("submission_asset_path_invalid", label);
  }
  const absolutePath = path.join(root, relativePath);
  const stats = fs.statSync(absolutePath, { throwIfNoEntry: false });
  if (!stats?.isFile()) fail("submission_asset_missing", `${label}:${relativePath}`);
  if (stats.size > 5 * 1024 * 1024) fail("submission_asset_too_large", `${label}:${stats.size}`);
  const bytes = fs.readFileSync(absolutePath);
  if (bytes.length < 24 || !bytes.subarray(0, 8).equals(PNG_SIGNATURE) || bytes.toString("ascii", 12, 16) !== "IHDR") {
    fail("submission_asset_not_png", label);
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width !== height || width < 48 || width > 4096) {
    fail("submission_asset_dimensions_invalid", `${label}:${width}x${height}`);
  }
}

function validateReviewCases(cases, label, exact, resultField) {
  if (!Array.isArray(cases) || cases.length !== exact) {
    fail("submission_review_case_count_invalid", `${label}:${cases?.length ?? "missing"}!=${exact}`);
  }
  cases.forEach((entry, index) => {
    requireObject(entry, `${label}[${index}]`);
    requireText(entry.prompt, `${label}[${index}].prompt`, { oneLine: true });
    requireText(entry.expectedBehavior, `${label}[${index}].expectedBehavior`);
    requireText(entry[resultField], `${label}[${index}].${resultField}`);
    if (label === "positiveTests") requireText(entry.fixture, `${label}[${index}].fixture`);
  });
}

function listFiles(root) {
  const files = [];
  let totalBytes = 0;
  const visit = (directory) => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const absolutePath = path.join(directory, entry.name);
      const relativePath = path.relative(root, absolutePath).split(path.sep).join("/");
      const stats = fs.lstatSync(absolutePath);
      if (stats.isSymbolicLink()) fail("submission_symlink_forbidden", relativePath);
      if (stats.isDirectory()) {
        visit(absolutePath);
      } else if (stats.isFile()) {
        if (stats.size > MAX_ARCHIVE_BYTES) fail("submission_file_too_large", relativePath);
        totalBytes += stats.size;
        files.push(relativePath);
      } else {
        fail("submission_file_type_unsupported", relativePath);
      }
    }
  };
  visit(root);
  if (files.length > MAX_ARCHIVE_ENTRIES) fail("submission_too_many_files", String(files.length));
  if (totalBytes > MAX_UNCOMPRESSED_BYTES) fail("submission_uncompressed_too_large", String(totalBytes));
  return files.sort();
}

function validateNoInternalContent(root, files) {
  for (const relativePath of files) {
    if (INTERNAL_PATH_PREFIXES.some((prefix) => relativePath === prefix || relativePath.startsWith(prefix))) {
      fail("submission_internal_path_leak", relativePath);
    }
    const extension = path.extname(relativePath).toLowerCase();
    if (![".json", ".md", ".mjs", ".js", ".ts", ".yaml", ".yml", ".txt"].includes(extension)) continue;
    if (relativePath === "tools/validate-submission.mjs") continue;
    const contents = fs.readFileSync(path.join(root, relativePath), "utf8");
    for (const marker of INTERNAL_TEXT_MARKERS) {
      if (contents.includes(marker)) fail("submission_internal_reference_leak", `${relativePath}:${marker}`);
    }
  }
}

function parseQuotedYamlValue(rawValue, relativePath, field) {
  const value = rawValue.trim();
  if (!value) fail("submission_skill_agent_value_empty", `${relativePath}:${field}`);
  if (value.startsWith('"')) {
    try {
      return JSON.parse(value);
    } catch {
      fail("submission_skill_agent_yaml_invalid", `${relativePath}:${field}`);
    }
  }
  if (value.startsWith("'") && value.endsWith("'")) return value.slice(1, -1).replace(/''/g, "'");
  return value;
}

function validateOpenAiSkillMetadata(root, files) {
  const allowedFields = new Set([
    "display_name",
    "short_description",
    "icon_small",
    "icon_large",
    "brand_color",
    "default_prompt",
  ]);
  const metadataFiles = files.filter((file) => /^skills\/[^/]+\/agents\/openai\.yaml$/.test(file));
  for (const relativePath of metadataFiles) {
    const contents = fs.readFileSync(path.join(root, relativePath), "utf8");
    if (contents.includes("\t")) fail("submission_skill_agent_tab_forbidden", relativePath);
    const interfaceBlock = contents.match(/^interface:\s*\r?\n((?:^[ \t]+.*(?:\r?\n|$))*)/m);
    if (!interfaceBlock) fail("submission_skill_agent_interface_missing", relativePath);
    const values = {};
    for (const line of interfaceBlock[1].split(/\r?\n/)) {
      if (!line.trim()) continue;
      const match = line.match(/^  ([a-z_]+):\s*(.*)$/);
      if (!match) fail("submission_skill_agent_yaml_invalid", relativePath);
      if (!allowedFields.has(match[1])) {
        fail("submission_skill_agent_field_unsupported", `${relativePath}:${match[1]}`);
      }
      values[match[1]] = parseQuotedYamlValue(match[2], relativePath, match[1]);
    }
    requireText(values.display_name, `${relativePath}:interface.display_name`, { oneLine: true });
    requireText(values.short_description, `${relativePath}:interface.short_description`, { oneLine: true });
    if (values.brand_color && !/^#[0-9A-Fa-f]{6}$/.test(values.brand_color)) {
      fail("submission_skill_agent_brand_color_invalid", relativePath);
    }
    if (values.default_prompt)
      requireText(values.default_prompt, `${relativePath}:interface.default_prompt`, { oneLine: true });
    for (const field of ["icon_small", "icon_large"]) {
      if (!values[field]) continue;
      if (!values[field].startsWith("./") || values[field].split("/").includes("..")) {
        fail("submission_skill_agent_icon_path_invalid", `${relativePath}:${field}`);
      }
      const skillRoot = path.dirname(path.dirname(path.join(root, relativePath)));
      if (!fs.statSync(path.resolve(skillRoot, values[field]), { throwIfNoEntry: false })?.isFile()) {
        fail("submission_skill_agent_icon_missing", `${relativePath}:${field}`);
      }
    }
  }
  return metadataFiles.length;
}

function validatePortablePackage(root, files) {
  const portableValidator = path.join(root, "tools", "validate-plugin.mjs");
  if (!fs.statSync(portableValidator, { throwIfNoEntry: false })?.isFile()) {
    fail("submission_portable_validator_missing");
  }
  const result = spawnSync(process.execPath, [portableValidator, root], { cwd: root, encoding: "utf8" });
  if (result.status !== 0) {
    fail("submission_portable_validation_failed", String(result.stderr || result.stdout).trim());
  }
  if (!files.includes(".claude-plugin/plugin.json")) fail("submission_openai_upload_manifest_missing");
  if (files.includes(".codex-plugin/plugin.json")) fail("submission_superseded_codex_manifest_present");
  if (files.includes(".cursor-plugin/plugin.json")) fail("submission_superseded_cursor_manifest_present");
  if (files.includes(".mcp.json") || files.includes(".app.json")) {
    fail("submission_skills_only_configuration_invalid");
  }
}

function validateClaude(root, manifest, metadata) {
  const claudeManifest = readJson(root, ".claude-plugin/plugin.json");
  const claudeMarketplace = readJson(root, ".claude-plugin/marketplace.json");
  if (claudeManifest.$schema !== "https://json.schemastore.org/claude-code-plugin-manifest.json") {
    fail("submission_claude_schema_missing");
  }
  if (claudeManifest.name !== manifest.name || claudeManifest.version !== manifest.version) {
    fail("submission_claude_manifest_identity_mismatch");
  }
  if (claudeManifest.displayName !== metadata.shared.displayName) {
    fail("submission_claude_display_name_mismatch");
  }
  requireObject(claudeMarketplace, "claudeMarketplace");
  const entry = claudeMarketplace.plugins?.find((candidate) => candidate?.name === manifest.name);
  if (!entry) fail("submission_claude_marketplace_entry_missing");
  if (entry.version !== manifest.version || entry.displayName !== metadata.claude.displayName) {
    fail("submission_claude_marketplace_identity_mismatch");
  }
  if (entry.category !== metadata.claude.category) fail("submission_claude_category_mismatch");
  if (JSON.stringify(entry.tags) !== JSON.stringify(metadata.claude.tags)) {
    fail("submission_claude_tags_mismatch");
  }
}

function validateCodexCatalog(root, manifest, metadata) {
  const catalog = readJson(root, ".agents/plugins/marketplace.json");
  const entry = catalog.plugins?.find((candidate) => candidate?.name === manifest.name);
  if (!entry) fail("submission_codex_catalog_entry_missing");
  if (catalog.interface?.displayName !== metadata.shared.displayName) {
    fail("submission_codex_display_name_mismatch");
  }
  if (entry.category !== metadata.openai.category) fail("submission_codex_category_mismatch");
}

export function validateSubmissionRoot(root) {
  const files = listFiles(root);
  validateNoInternalContent(root, files);
  validatePortablePackage(root, files);
  const openAiSkillMetadataCount = validateOpenAiSkillMetadata(root, files);

  const manifest = readJson(root, "plugin.json");
  const metadata = readJson(root, "submission/marketplaces.json");
  requireObject(metadata, "metadata");
  requireObject(metadata.shared, "shared");
  requireObject(metadata.openai, "openai");
  requireObject(metadata.cursor, "cursor");
  requireObject(metadata.claude, "claude");

  const { shared, openai, cursor, claude } = metadata;
  requireText(shared.displayName, "shared.displayName", { oneLine: true, max: 30 });
  requireText(shared.developerName, "shared.developerName", { oneLine: true, max: 80 });
  for (const field of [
    "websiteURL",
    "documentationURL",
    "supportURL",
    "privacyPolicyURL",
    "termsOfServiceURL",
    "repositoryURL",
  ]) {
    requireHttpsUrl(shared[field], `shared.${field}`);
  }
  validatePng(root, shared.logo, "shared.logo");

  if (openai.submissionType !== "skills-only") fail("submission_openai_type_invalid");
  requireText(openai.shortDescription, "openai.shortDescription", { oneLine: true, max: 30 });
  requireText(openai.longDescription, "openai.longDescription", { max: 4000 });
  if (!OPENAI_CATEGORIES.has(openai.category)) fail("submission_openai_category_invalid", openai.category);
  requireStringList(openai.capabilities, "openai.capabilities", { max: 20, oneLine: true, entryMax: 120 });
  validateColor(openai.brandColor, "openai.brandColor", "#FFFFFF");
  validateColor(openai.brandColorDark, "openai.brandColorDark", "#212121");
  validatePng(root, openai.composerIcon, "openai.composerIcon");
  requireStringList(openai.starterPrompts, "openai.starterPrompts", { max: 3, oneLine: true, entryMax: 128 });
  const normalizedPrompts = new Set();
  for (const prompt of openai.starterPrompts) {
    if (/@/.test(prompt)) fail("submission_openai_prompt_mention", prompt);
    const normalized = prompt.normalize("NFKC").trim().replace(/\s+/g, " ").toLocaleLowerCase("en-US");
    if (normalizedPrompts.has(normalized)) fail("submission_openai_prompt_duplicate", prompt);
    normalizedPrompts.add(normalized);
  }
  validateReviewCases(openai.positiveTests, "positiveTests", 5, "expectedResultShape");
  validateReviewCases(openai.negativeTests, "negativeTests", 3, "rationale");
  requireText(openai.releaseNotes, "openai.releaseNotes");

  if (cursor.displayName !== shared.displayName || cursor.publisher !== shared.developerName) {
    fail("submission_cursor_identity_mismatch");
  }
  requireText(cursor.organizationName, "cursor.organizationName", { oneLine: true });
  requireText(cursor.organizationHandle, "cursor.organizationHandle", { oneLine: true });
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(cursor.organizationHandle)) {
    fail("submission_cursor_handle_invalid");
  }
  requireText(cursor.contactEmail, "cursor.contactEmail", { oneLine: true });
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(cursor.contactEmail)) fail("submission_cursor_email_invalid");
  requireHttpsUrl(cursor.logoURL, "cursor.logoURL");
  requireText(cursor.description, "cursor.description", { oneLine: true });
  requireText(cursor.category, "cursor.category", { oneLine: true });
  requireStringList(cursor.tags, "cursor.tags", { oneLine: true });
  if (claude.displayName !== shared.displayName) fail("submission_claude_metadata_identity_mismatch");
  requireText(claude.category, "claude.category", { oneLine: true });
  requireStringList(claude.tags, "claude.tags", { oneLine: true });

  if (manifest.author?.name !== shared.developerName) fail("submission_developer_name_mismatch");
  if (manifest.repository !== shared.repositoryURL || manifest.homepage !== shared.websiteURL) {
    fail("submission_portable_urls_mismatch");
  }
  validateClaude(root, manifest, metadata);
  validateCodexCatalog(root, manifest, metadata);

  const skillCount = files.filter((file) => /^skills\/[^/]+\/SKILL\.md$/.test(file)).length;
  return { manifest, metadata, skillCount, openAiSkillMetadataCount };
}

function validateArchivePaths(zipPath) {
  const stats = fs.statSync(zipPath, { throwIfNoEntry: false });
  if (!stats?.isFile()) fail("submission_archive_missing", zipPath);
  if (stats.size > MAX_ARCHIVE_BYTES) fail("submission_archive_too_large", String(stats.size));
  const list = spawnSync("unzip", ["-Z1", zipPath], { encoding: "utf8" });
  if (list.status !== 0) fail("submission_archive_invalid", String(list.stderr || list.stdout).trim());
  const entries = list.stdout.split(/\r?\n/).filter(Boolean);
  if (entries.length === 0) fail("submission_archive_empty");
  if (entries.length > MAX_ARCHIVE_ENTRIES) fail("submission_too_many_entries", String(entries.length));
  const normalized = new Set();
  for (const entry of entries) {
    if (entry !== entry.trim()) fail("submission_archive_path_whitespace", entry);
    if (entry.includes("\\")) fail("submission_archive_path_backslash", entry);
    if (entry.startsWith("/") || /^[A-Za-z]:/.test(entry)) fail("submission_archive_path_absolute", entry);
    const segments = entry.split("/").filter((segment, index, all) => !(index === all.length - 1 && segment === ""));
    if (segments.some((segment) => !segment || segment === ".."))
      fail("submission_archive_path_segment_invalid", entry);
    if (segments.length > 20 || entry.length > 1024) fail("submission_archive_path_limit", entry);
    const key = entry.normalize("NFC").toLocaleLowerCase("en-US");
    if (normalized.has(key)) fail("submission_archive_path_collision", entry);
    normalized.add(key);
  }
}

function resolveInput(input) {
  const resolved = path.resolve(input);
  if (path.extname(resolved).toLowerCase() !== ".zip") return { root: resolved, cleanup: null };
  validateArchivePaths(resolved);
  const temporaryRoot = fs.mkdtempSync(path.join(os.tmpdir(), "playdrop-submission-"));
  const extract = spawnSync("unzip", ["-qq", resolved, "-d", temporaryRoot], { encoding: "utf8" });
  if (extract.status !== 0) {
    fs.rmSync(temporaryRoot, { recursive: true, force: true });
    fail("submission_archive_extract_failed", String(extract.stderr || extract.stdout).trim());
  }
  return { root: temporaryRoot, cleanup: () => fs.rmSync(temporaryRoot, { recursive: true, force: true }) };
}

function runClaudeValidation(root) {
  const result = spawnSync("claude", ["plugin", "validate", "--strict", root], {
    cwd: root,
    encoding: "utf8",
    maxBuffer: 8 * 1024 * 1024,
  });
  if (result.error?.code === "ENOENT") fail("submission_claude_cli_missing");
  if (result.status !== 0) {
    fail("submission_claude_validation_failed", String(result.stderr || result.stdout).trim());
  }
}

async function main() {
  const defaultRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
  const target = resolveInput(process.argv[2] || defaultRoot);
  try {
    const result = validateSubmissionRoot(target.root);
    runClaudeValidation(target.root);
    process.stdout.write(
      `submission_valid:${result.manifest.name}:${result.manifest.version}:skills=${result.skillCount}:openai-metadata=${result.openAiSkillMetadataCount}:cursor=portable-metadata:claude=strict\n`,
    );
  } finally {
    target.cleanup?.();
  }
}

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1]);
if (isMain) {
  main().catch((error) => {
    process.stderr.write(`${error instanceof Error ? error.message : String(error)}\n`);
    process.exitCode = 1;
  });
}
