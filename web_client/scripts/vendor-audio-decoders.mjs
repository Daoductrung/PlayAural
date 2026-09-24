import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const packageName = "stb-vorbis";
const sourcePackage = path.join(webRoot, "node_modules", packageName);
const source = path.join(sourcePackage, "dist", "index.js");
const destination = path.join(webRoot, "vendor", "stb-vorbis.js");

if (!fs.existsSync(source)) {
  throw new Error("Install web_client dependencies before vendoring the Vorbis decoder.");
}

const projectPackage = JSON.parse(fs.readFileSync(
  path.join(webRoot, "package.json"),
  "utf8",
));
const decoderPackage = JSON.parse(fs.readFileSync(
  path.join(sourcePackage, "package.json"),
  "utf8",
));
const expectedVersion = projectPackage.dependencies?.[packageName];
if (!expectedVersion || decoderPackage.version !== expectedVersion) {
  throw new Error(
    `Expected ${packageName} ${expectedVersion || "to be pinned"}, found ${decoderPackage.version}.`,
  );
}

fs.copyFileSync(source, destination);
console.log(
  `Copied ${path.relative(webRoot, destination)} from ${packageName} ${decoderPackage.version}.`,
);
