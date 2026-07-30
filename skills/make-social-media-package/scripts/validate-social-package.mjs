#!/usr/bin/env node

import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { resolve } from 'node:path';
import { spawnSync } from 'node:child_process';

const root = resolve(process.argv[2] || '');
if (!process.argv[2]) {
  console.error('usage: validate-social-package.mjs <social-media-directory>');
  process.exit(2);
}

const expected = [
  ['video', 'short/portrait-9x16.mp4', 1080, 1920],
  ['video', 'short/pinterest-2x3.mp4', 1000, 1500],
  ['video', 'trailer/landscape-16x9.mp4', 1920, 1080],
  ['video', 'instagram/feed/video-3x4.mp4', 1080, 1440],
  ['image', 'instagram/reels-cover-420x654.png', 420, 654],
  ['image', 'youtube/trailer-thumbnail-1280x720.png', 1280, 720],
];

let failed = false;

function fail(message) {
  failed = true;
  console.error(`FAIL ${message}`);
}

function pass(message) {
  console.log(`PASS ${message}`);
}

function probe(relativePath) {
  const file = resolve(root, relativePath);
  const result = spawnSync(
    'ffprobe',
    [
      '-v',
      'error',
      '-show_entries',
      'format=duration',
      '-show_entries',
      'stream=codec_type,codec_name,width,height,sample_aspect_ratio,r_frame_rate,channels,sample_rate',
      '-of',
      'json',
      file,
    ],
    { encoding: 'utf8' },
  );
  if (result.status !== 0) {
    throw new Error(result.stderr.trim() || `ffprobe failed for ${relativePath}`);
  }
  return JSON.parse(result.stdout);
}

for (const [kind, relativePath, width, height] of expected) {
  const file = resolve(root, relativePath);
  if (!existsSync(file)) {
    fail(`missing ${relativePath}`);
    continue;
  }
  try {
    const data = probe(relativePath);
    const video = data.streams.find((stream) => stream.codec_type === 'video');
    const audio = data.streams.find((stream) => stream.codec_type === 'audio');
    if (!video || video.width !== width || video.height !== height) {
      fail(`${relativePath} expected ${width}x${height}, got ${video?.width ?? 0}x${video?.height ?? 0}`);
      continue;
    }
    if (video.sample_aspect_ratio && video.sample_aspect_ratio !== '1:1') {
      fail(`${relativePath} sample aspect ratio is ${video.sample_aspect_ratio}, expected 1:1`);
      continue;
    }
    if (kind === 'video') {
      if (video.codec_name !== 'h264') {
        fail(`${relativePath} expected H.264, got ${video.codec_name}`);
        continue;
      }
      if (!audio || audio.codec_name !== 'aac' || audio.channels !== 2) {
        fail(`${relativePath} expected AAC stereo audio`);
        continue;
      }
    }
    pass(`${relativePath} ${width}x${height}`);
  } catch (error) {
    fail(`${relativePath}: ${error.message}`);
  }
}

for (const [relativeDirectory, width, height] of [
  ['pinterest/static', 1000, 1500],
  ['instagram/feed/carousel', 1080, 1440],
]) {
  const directory = resolve(root, relativeDirectory);
  if (!existsSync(directory)) {
    fail(`missing ${relativeDirectory}`);
    continue;
  }
  const files = readdirSync(directory).filter((file) => file.endsWith('.png')).sort();
  if (files.length !== 5) {
    fail(`${relativeDirectory} expected 5 PNG files, got ${files.length}`);
  }
  for (const file of files) {
    const relativePath = `${relativeDirectory}/${file}`;
    try {
      const data = probe(relativePath);
      const image = data.streams.find((stream) => stream.codec_type === 'video');
      if (!image || image.width !== width || image.height !== height) {
        fail(`${relativePath} expected ${width}x${height}, got ${image?.width ?? 0}x${image?.height ?? 0}`);
      } else {
        pass(`${relativePath} ${width}x${height}`);
      }
    } catch (error) {
      fail(`${relativePath}: ${error.message}`);
    }
  }
}

const manifestPath = resolve(root, 'manifest.json');
if (!existsSync(manifestPath)) {
  fail('missing manifest.json');
} else {
  try {
    const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'));
    for (const field of ['youtube', 'tiktok', 'instagram', 'pinterest', 'x']) {
      if (!manifest[field]) fail(`manifest missing ${field}`);
    }
    if (!manifest.destinationUrl?.startsWith('https://www.playdrop.ai/')) {
      fail('manifest destinationUrl must be a canonical PlayDrop URL');
    } else {
      pass('manifest channel mapping and destination URL');
    }
  } catch (error) {
    fail(`manifest.json: ${error.message}`);
  }
}

console.log('NOTE Technical validation cannot detect bars, filler, or clipped content. Complete the required visual review.');
process.exit(failed ? 1 : 0);
