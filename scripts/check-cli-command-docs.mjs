#!/usr/bin/env node

import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const pluginRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const monorepoRoot = resolve(pluginRoot, '..', 'playdrop');
const cliEntry = process.env.PLAYDROP_CLI_ENTRY
  ? resolve(process.env.PLAYDROP_CLI_ENTRY)
  : resolve(monorepoRoot, 'packages', 'playdrop-cli', 'dist', 'index.js');

if (!existsSync(cliEntry)) {
  console.error(`CLI entry not found: ${cliEntry}`);
  console.error('Build the monorepo CLI first: npm --workspace @playdrop/playdrop-cli run build -- --pretty false');
  process.exit(1);
}

const stagingPath = resolve(pluginRoot, 'playdrop-worker-staging.json');
const staging = JSON.parse(readFileSync(stagingPath, 'utf8'));
const stagedFiles = new Set(Object.values(staging.taskFiles ?? {}).flat());

const COMMAND_PATHS = [
  ['project', 'create', 'app'],
  ['project', 'capture', 'remote'],
  ['project', 'capture'],
  ['project', 'check'],
  ['project', 'validate'],
  ['ai', 'create'],
  ['task', 'report-catalogue'],
  ['task', 'submit-review'],
  ['task', 'submit-eval'],
  ['task', 'report'],
  ['task', 'upload'],
  ['task', 'done'],
  ['task', 'fail'],
  ['review', 'list-windows'],
  ['review', 'screenshot'],
  ['review', 'compose-evidence'],
  ['review', 'rating-card'],
  ['review', 'validate-result'],
  ['versions', 'browse'],
  ['help'],
  ['search'],
  ['browse'],
  ['detail'],
];

const replacements = new Map([
  ['<slug>', 'sample-game'],
  ['<allowed-template-key>', 'playdrop/template/html_single_file_template'],
  ['<source-ref>', 'playdrop/sample-game@1.0.0'],
  ['<surface>', 'desktop'],
  ['<path>', '.tmp/output.json'],
  ['<STATE>', 'NEEDS_WORK'],
  ['<dir>', '.tmp/evidence'],
  ['<phase>', 'core-loop'],
  ['<what changed>', 'Built the loop'],
  ['<what is happening now>', 'Playtesting'],
  ['<creator-friendly reason>', 'Validation failed'],
  ['<genre>', 'racing'],
  ['<genre or theme>', 'racing'],
  ['<pack-name>', 'racing-kit-repack'],
]);

function tokenize(command) {
  const replaced = Array.from(replacements.entries()).reduce(
    (text, [needle, value]) => text.split(needle).join(value),
    command.replace(/\\\s*$/, '').trim(),
  );
  const matches = replaced.match(/"[^"]*"|'[^']*'|\S+/g) ?? [];
  return matches.map((token) => token.replace(/^["']|["']$/g, ''));
}

function findCommandPath(args) {
  for (const path of COMMAND_PATHS) {
    if (path.every((part, index) => args[index] === part)) {
      return path;
    }
  }
  return null;
}

const helpCache = new Map();
function readHelp(commandPath) {
  const key = commandPath.join(' ');
  if (helpCache.has(key)) {
    return helpCache.get(key);
  }
  const result = spawnSync(process.execPath, [cliEntry, ...commandPath, '--help'], {
    encoding: 'utf8',
    cwd: pluginRoot,
  });
  if (result.status !== 0) {
    throw new Error(`CLI help failed for "${key}": ${result.stderr || result.stdout}`);
  }
  const help = `${result.stdout}\n${result.stderr}`;
  helpCache.set(key, help);
  return help;
}

const failures = [];
const seen = new Set();

for (const relativePath of stagedFiles) {
  const absolutePath = resolve(pluginRoot, relativePath);
  if (!existsSync(absolutePath)) {
    failures.push(`${relativePath}: staged file is missing`);
    continue;
  }
  const text = readFileSync(absolutePath, 'utf8');
  const commandRegex = /(?:^|[` \t])((?:\.\/bin\/)?playdrop(?:\s+[^`\n]*)?)/gm;
  for (const match of text.matchAll(commandRegex)) {
    const raw = match[1].trim();
    if (!raw || raw.includes('playdrop.ai') || raw.includes('...')) {
      continue;
    }
    const tokens = tokenize(raw);
    if (tokens[0] === './bin/playdrop' || tokens[0] === 'playdrop') {
      tokens.shift();
    }
    if (tokens.length === 0) {
      continue;
    }
    const commandPath = findCommandPath(tokens);
    if (!commandPath) {
      failures.push(`${relativePath}: unknown documented command "${raw}"`);
      continue;
    }
    const key = `${relativePath}:${raw}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    let help;
    try {
      help = readHelp(commandPath);
    } catch (error) {
      failures.push(`${relativePath}: ${error.message}`);
      continue;
    }
    const documentedOptions = tokens
      .slice(commandPath.length)
      .filter((token) => token.startsWith('--'))
      .map((token) => token.split('=')[0]);
    for (const option of documentedOptions) {
      if (!help.includes(option)) {
        failures.push(`${relativePath}: option ${option} is not accepted by "${commandPath.join(' ')}"`);
      }
    }
  }
}

if (failures.length > 0) {
  console.error('Documented PlayDrop CLI command check failed:');
  for (const failure of failures) {
    console.error(`- ${failure}`);
  }
  process.exit(1);
}

console.log(`Checked documented PlayDrop CLI commands in ${stagedFiles.size} staged files.`);
