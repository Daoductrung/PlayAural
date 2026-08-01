import { readFile, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const UPSTREAM_ROUTE_UPDATE =
  "      updatePlaySoundThroughEarpiece(mode.shouldRouteThroughEarpiece ?: false)";
const GUARDED_ROUTE_UPDATE = [
  "      mode.shouldRouteThroughEarpiece?.let { shouldRouteThroughEarpiece ->",
  "        updatePlaySoundThroughEarpiece(shouldRouteThroughEarpiece)",
  "      }",
].join("\n");

export function patchExpoAudioRouting(source) {
  const upstreamMatches = source.split(UPSTREAM_ROUTE_UPDATE).length - 1;
  const guardedMatches = source.split(GUARDED_ROUTE_UPDATE).length - 1;

  if (upstreamMatches === 0 && guardedMatches === 1) {
    return { changed: false, source };
  }
  if (upstreamMatches !== 1 || guardedMatches !== 0) {
    throw new Error(
      "Unsupported expo-audio AudioModule.kt routing implementation. "
        + "Review the installed dependency before building PlayAural.",
    );
  }

  return {
    changed: true,
    source: source.replace(UPSTREAM_ROUTE_UPDATE, GUARDED_ROUTE_UPDATE),
  };
}

export function resolveExpoAudioModulePath() {
  const require = createRequire(import.meta.url);
  const packagePath = require.resolve("expo-audio/package.json");
  return resolve(
    dirname(packagePath),
    "android/src/main/java/expo/modules/audio/AudioModule.kt",
  );
}

async function main() {
  const modulePath = resolveExpoAudioModulePath();
  const source = await readFile(modulePath, "utf8");
  const result = patchExpoAudioRouting(source);
  if (result.changed) {
    await writeFile(modulePath, result.source, "utf8");
    console.log("Patched expo-audio to preserve Android's selected output route.");
    return;
  }
  console.log("expo-audio Android output routing is already protected.");
}

const invokedPath = process.argv[1] ? resolve(process.argv[1]) : null;
if (invokedPath === fileURLToPath(import.meta.url)) {
  await main();
}
