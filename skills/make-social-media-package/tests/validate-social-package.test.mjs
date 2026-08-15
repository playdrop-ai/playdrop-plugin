import assert from "node:assert/strict";
import { cp, mkdtemp, mkdir, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import test from "node:test";

const validator = resolve(
  "plugins/playdrop-creator/skills/make-social-media-package/scripts/validate-social-package.mjs",
);

function run(command, args) {
  const result = spawnSync(command, args, { encoding: "utf8" });
  assert.equal(result.status, 0, result.stderr || result.stdout);
}

async function makeFixture() {
  const root = await mkdtemp(join(tmpdir(), "playdrop-social-package-"));
  await mkdir(join(root, "video"), { recursive: true });
  await mkdir(join(root, "images"), { recursive: true });

  run("ffmpeg", [
    "-v",
    "error",
    "-y",
    "-f",
    "lavfi",
    "-i",
    "color=c=black:s=1920x1080:r=1:d=30",
    "-f",
    "lavfi",
    "-i",
    "anullsrc=channel_layout=stereo:sample_rate=48000",
    "-t",
    "30",
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
    "-c:a",
    "aac",
    join(root, "video", "trailer.mp4"),
  ]);
  run("ffmpeg", [
    "-v",
    "error",
    "-y",
    "-f",
    "lavfi",
    "-i",
    "color=c=black:s=1080x1920:r=1:d=12",
    "-f",
    "lavfi",
    "-i",
    "anullsrc=channel_layout=stereo:sample_rate=48000",
    "-t",
    "12",
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
    "-c:a",
    "aac",
    join(root, "video", "short.mp4"),
  ]);
  run("ffmpeg", [
    "-v",
    "error",
    "-y",
    "-f",
    "lavfi",
    "-i",
    "color=c=black:s=90x160",
    "-frames:v",
    "1",
    join(root, "images", "1.png"),
  ]);
  for (let index = 2; index <= 4; index += 1) {
    await cp(join(root, "images", "1.png"), join(root, "images", `${index}.png`));
  }

  return root;
}

test("accepts the standard four-channel package with shared canonical media", async () => {
  const root = await makeFixture();
  const manifest = {
    destinationUrl: "https://www.playdrop.ai/@studio/game",
    youtube: {
      trailerVideo: "video/trailer.mp4",
      shortVideo: "video/short.mp4",
      trailerTitle: "Game trailer",
      shortTitle: "Game short",
      description: "Play the game.",
    },
    tiktok: { video: "video/short.mp4", caption: "Play now." },
    instagram: {
      reelVideo: "video/short.mp4",
      storyVideo: "video/short.mp4",
      images: ["images/1.png", "images/2.png", "images/3.png", "images/4.png"],
      caption: "Play now.",
    },
    x: { video: "video/trailer.mp4", copy: "Play now." },
  };
  await writeFile(join(root, "manifest.json"), JSON.stringify(manifest));

  const result = spawnSync("node", [validator, root], { encoding: "utf8" });
  assert.equal(result.status, 0, result.stderr || result.stdout);
  assert.match(result.stdout, /PASS social package structure and media/);
});

test("rejects a package that duplicates the wrong video mapping", async () => {
  const root = await makeFixture();
  await writeFile(
    join(root, "manifest.json"),
    JSON.stringify({
      destinationUrl: "https://www.playdrop.ai/@studio/game",
      youtube: {
        trailerVideo: "video/trailer.mp4",
        shortVideo: "video/short.mp4",
        trailerTitle: "Game trailer",
        shortTitle: "Game short",
        description: "Play the game.",
      },
      tiktok: { video: "video/trailer.mp4", caption: "Play now." },
      instagram: {
        reelVideo: "video/short.mp4",
        storyVideo: "video/short.mp4",
        images: ["images/1.png", "images/2.png", "images/3.png", "images/4.png"],
        caption: "Play now.",
      },
      x: { video: "video/trailer.mp4", copy: "Play now." },
    }),
  );

  const result = spawnSync("node", [validator, root], { encoding: "utf8" });
  assert.equal(result.status, 1);
  assert.match(result.stderr, /tiktok.video must reuse youtube.shortVideo/);
});
