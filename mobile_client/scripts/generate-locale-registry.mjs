import { readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(scriptDir, "..");
const localesRoot = path.join(projectRoot, "locales");
const metadataPath = path.join(localesRoot, "metadata.json");
const outputPath = path.join(projectRoot, "src", "i18n", "localeCatalogs.ts");

function assertLocaleCode(code) {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/u.test(code)) {
    throw new Error(`Unsafe locale code: ${code}`);
  }
}

function formatStringArray(values) {
  return `[${values.map((value) => JSON.stringify(value)).join(", ")}]`;
}

const metadata = JSON.parse(await readFile(metadataPath, "utf8"));
const localeDirs = (await readdir(localesRoot, { withFileTypes: true }))
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();

if (!localeDirs.includes(metadata.defaultLocale)) {
  throw new Error(`Default locale ${metadata.defaultLocale} has no catalog directory.`);
}

const imports = [];
const metadataEntries = [];
const catalogEntries = [];

for (const code of localeDirs) {
  assertLocaleCode(code);
  const catalogPath = path.join(localesRoot, code, "client.json");
  await readFile(catalogPath, "utf8");
  const binding = `catalog_${code.replaceAll("-", "_")}`;
  imports.push(`import ${binding} from "../../locales/${code}/client.json";`);

  const info = metadata.locales?.[code] ?? {};
  metadataEntries.push(`  ${JSON.stringify(code)}: {
    name: ${JSON.stringify(info.name ?? code)},
    nativeName: ${JSON.stringify(info.nativeName ?? info.name ?? code)},
    contributors: ${formatStringArray(info.contributors ?? [])},
    official: ${info.official === true ? "true" : "false"},
  },`);
  catalogEntries.push(`  ${JSON.stringify(code)}: ${binding},`);
}

const content = `${imports.join("\n")}

export const DEFAULT_LOCALE = ${JSON.stringify(metadata.defaultLocale)};

export const LOCALE_METADATA = {
${metadataEntries.join("\n")}
} as const;

export const localeCatalogs = {
${catalogEntries.join("\n")}
} as const;

export type MobileLocale = keyof typeof localeCatalogs;
`;

await writeFile(outputPath, content, "utf8");
console.log(`Generated ${path.relative(projectRoot, outputPath)} for ${localeDirs.length} locales.`);
