#!/usr/bin/env node

import { existsSync, readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(process.argv[2] || "");
if (!process.argv[2]) {
  console.error("usage: validate-social-package.mjs <social-media-directory>");
  process.exit(2);
}

const manifestPath = resolve(root, "manifest.json");
if (!existsSync(manifestPath)) {
  console.error("FAIL missing manifest.json");
  process.exit(1);
}

let manifest;
try {
  manifest = JSON.parse(readFileSync(manifestPath, "utf8"));
} catch (error) {
  console.error(`FAIL invalid manifest.json: ${error.message}`);
  process.exit(1);
}
let failed = false;

function fail(message) {
  failed = true;
  console.error(`FAIL ${message}`);
}

function mediaPath(value, field) {
  if (typeof value !== "string" || value.length === 0) {
    fail(`manifest missing ${field}`);
    return null;
  }
  const path = resolve(dirname(manifestPath), value);
  if (!existsSync(path)) {
    fail(`${field} does not resolve: ${value}`);
    return null;
  }
  return path;
}

function probe(path, field) {
  const result = spawnSync(
    "ffprobe",
    [
      "-v",
      "error",
      "-show_entries",
      "format=duration,bit_rate",
      "-show_entries",
      "stream=codec_type,codec_name,width,height,sample_aspect_ratio,avg_frame_rate,channels,sample_rate",
      "-of",
      "json",
      path,
    ],
    { encoding: "utf8" },
  );
  if (result.status !== 0) {
    fail(`${field}: ${result.stderr.trim() || "ffprobe failed"}`);
    return null;
  }
  return JSON.parse(result.stdout);
}

function frameRate(value) {
  if (typeof value !== "string") return Number.NaN;
  const [numerator, denominator = "1"] = value.split("/").map(Number);
  return denominator === 0 ? Number.NaN : numerator / denominator;
}

function validateVideo(value, field, width, height, minDuration, maxDuration) {
  const path = mediaPath(value, field);
  if (!path) return;
  const data = probe(path, field);
  if (!data) return;
  const video = data.streams.find((stream) => stream.codec_type === "video");
  const audio = data.streams.find((stream) => stream.codec_type === "audio");
  const duration = Number(data.format.duration);
  if (!video || video.width !== width || video.height !== height) {
    fail(`${field} must be ${width}x${height}`);
  } else if (video.codec_name !== "h264" || video.sample_aspect_ratio !== "1:1") {
    fail(`${field} must be H.264 with 1:1 sample aspect ratio`);
  }
  const fps = frameRate(video?.avg_frame_rate);
  if (!Number.isFinite(fps) || fps < 29 || fps > 31) {
    fail(`${field} must be 30 fps`);
  }
  const sampleRate = Number(audio?.sample_rate);
  if (!audio || audio.codec_name !== "aac" || audio.channels !== 2 || ![44100, 48000].includes(sampleRate)) {
    fail(`${field} must have AAC stereo audio at 44.1 or 48 kHz`);
  }
  if (!Number.isFinite(duration) || duration < minDuration || duration > maxDuration) {
    fail(`${field} duration must be between ${minDuration} and ${maxDuration} seconds`);
  }
  if (!Number.isFinite(Number(data.format.bit_rate)) || Number(data.format.bit_rate) <= 0) {
    fail(`${field} must report a positive bitrate`);
  }
}

const trailer = manifest.youtube?.trailerVideo;
const short = manifest.youtube?.shortVideo;
validateVideo(trailer, "youtube.trailerVideo", 1920, 1080, 30, 60);
validateVideo(short, "youtube.shortVideo", 1080, 1920, 8, 15);

if (manifest.x?.video !== trailer) fail("x.video must reuse youtube.trailerVideo");
if (manifest.tiktok?.video !== short) fail("tiktok.video must reuse youtube.shortVideo");
if (manifest.instagram?.reelVideo !== short) fail("instagram.reelVideo must reuse youtube.shortVideo");
if (manifest.instagram?.storyVideo !== short) fail("instagram.storyVideo must reuse youtube.shortVideo");

const images = manifest.instagram?.images;
if (!Array.isArray(images) || images.length !== 4) {
  fail("instagram.images must contain exactly four files");
} else {
  images.forEach((value, index) => {
    const field = `instagram.images[${index}]`;
    const path = mediaPath(value, field);
    if (!path) return;
    const data = probe(path, field);
    const image = data?.streams.find((stream) => stream.codec_type === "video");
    if (!image || Math.abs(image.width / image.height - 9 / 16) > 0.01) {
      fail(`${field} must be a 9:16 portrait image`);
    }
  });
}

if (typeof manifest.destinationUrl !== "string" || !manifest.destinationUrl.startsWith("https://www.playdrop.ai/")) {
  fail("destinationUrl must be a canonical PlayDrop URL");
}

for (const field of [
  ["youtube.trailerTitle", manifest.youtube?.trailerTitle],
  ["youtube.shortTitle", manifest.youtube?.shortTitle],
  ["youtube.description", manifest.youtube?.description],
  ["tiktok.caption", manifest.tiktok?.caption],
  ["instagram.caption", manifest.instagram?.caption],
  ["x.copy", manifest.x?.copy],
]) {
  if (typeof field[1] !== "string" || field[1].length === 0) fail(`manifest missing ${field[0]}`);
}

if (!failed) console.log("PASS social package structure and media");
console.log("NOTE Complete visual review is still required.");
process.exit(failed ? 1 : 0);
