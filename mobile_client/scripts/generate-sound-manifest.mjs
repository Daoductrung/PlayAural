import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const soundsDir = path.join(root, "sounds");
const outputFile = path.join(root, "src", "generated", "soundManifest.ts");
const versionFile = path.join(soundsDir, "version.txt");

function walk(dir, out = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full, out);
    } else if (/\.(ogg|wav|mp3)$/i.test(entry.name)) {
      out.push(full);
    }
  }
  return out;
}

if (!fs.existsSync(soundsDir)) {
  throw new Error(`Missing sounds directory: ${soundsDir}`);
}

const files = walk(soundsDir).sort();
const relativeAssets = files.map((file) => (
  path.relative(soundsDir, file).replaceAll("\\", "/")
));
const families = new Map();
for (const asset of relativeAssets) {
  const match = /^(.*?)([1-9][0-9]*)\.(ogg|wav|mp3)$/i.exec(asset);
  if (!match) {
    continue;
  }
  const entries = families.get(match[1]) || [];
  entries.push({ asset, index: Number(match[2]) });
  families.set(match[1], entries);
}
const soundPackVersion = fs.existsSync(versionFile)
  ? fs.readFileSync(versionFile, "utf8").trim()
  : "";
const lines = [
  "// Numbered entries are lookup candidates only; exact asset playback remains exact.",
  `export const bundledSoundVersion = ${JSON.stringify(soundPackVersion)};`,
  "",
  "export const soundManifest: Record<string, number> = {",
  ...relativeAssets.map((asset) => {
    const requirePath = "../../sounds/" + asset;
    return `  ${JSON.stringify(asset)}: require(${JSON.stringify(requirePath)}),`;
  }),
  "};",
  "",
  "export const soundFamilies: Readonly<Record<string, readonly string[]>> = {",
  ...[...families.entries()].sort(([left], [right]) => left.localeCompare(right)).map(
    ([family, entries]) => {
      const variants = entries
        .sort((left, right) => left.index - right.index || left.asset.localeCompare(right.asset))
        .map(({ asset }) => JSON.stringify(asset))
        .join(", ");
      return `  ${JSON.stringify(family)}: [${variants}],`;
    },
  ),
  "};",
  "",
];

fs.mkdirSync(path.dirname(outputFile), { recursive: true });
fs.writeFileSync(outputFile, lines.join("\n"), "utf8");
console.log(`Wrote ${files.length} sound entries to ${outputFile}`);
