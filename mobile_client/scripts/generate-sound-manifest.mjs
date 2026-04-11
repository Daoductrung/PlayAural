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
const soundPackVersion = fs.existsSync(versionFile)
  ? fs.readFileSync(versionFile, "utf8").trim()
  : "";
const lines = [
  `export const bundledSoundVersion = ${JSON.stringify(soundPackVersion)};`,
  "",
  "export const soundManifest: Record<string, number> = {",
  ...files.map((file) => {
    const relative = path.relative(soundsDir, file).replaceAll("\\", "/");
    const requirePath = "../../sounds/" + relative;
    return `  ${JSON.stringify(relative)}: require(${JSON.stringify(requirePath)}),`;
  }),
  "};",
  "",
];

fs.mkdirSync(path.dirname(outputFile), { recursive: true });
fs.writeFileSync(outputFile, lines.join("\n"), "utf8");
console.log(`Wrote ${files.length} sound entries to ${outputFile}`);
