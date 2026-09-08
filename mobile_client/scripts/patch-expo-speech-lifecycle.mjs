import { createHash } from "node:crypto";
import { readFile, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// Full-file guard: a dependency upgrade must be reviewed before this native
// lifecycle replacement can be applied. Normalize only checkout line endings.
const UPSTREAM_SHA256 = "7188d8b7f01e50e384770206b26d519e7ee0d40e9691026b322c7c5901a4908b";
export const replacementPath = fileURLToPath(new URL("../patches/expo-speech/SpeechModule.kt", import.meta.url));
const normalized = (source) => source.replaceAll("\r\n", "\n");

export function patchExpoSpeechLifecycle(source, replacement) {
  if (normalized(source) === normalized(replacement)) return { changed: false, source };
  const hash = createHash("sha256").update(normalized(source)).digest("hex");
  if (hash !== UPSTREAM_SHA256) {
    throw new Error("Unsupported expo-speech SpeechModule.kt. Review the native lifecycle before building PlayAural.");
  }
  return { changed: true, source: replacement };
}

export function resolveExpoSpeechModulePath() {
  const require = createRequire(import.meta.url);
  return resolve(dirname(require.resolve("expo-speech/package.json")), "android/src/main/java/expo/modules/speech/SpeechModule.kt");
}

async function main() {
  const path = resolveExpoSpeechModulePath();
  const result = patchExpoSpeechLifecycle(await readFile(path, "utf8"), await readFile(replacementPath, "utf8"));
  if (result.changed) await writeFile(path, result.source, "utf8");
  console.log("expo-speech Android lifecycle is protected.");
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
