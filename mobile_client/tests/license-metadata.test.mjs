import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";


test("every resolved mobile package declares public license metadata", async () => {
  const lock = JSON.parse(await readFile(
    new URL("../package-lock.json", import.meta.url),
    "utf8",
  ));
  const missing = Object.entries(lock.packages)
    .filter(([path]) => path.startsWith("node_modules/"))
    .filter(([, metadata]) => (
      typeof metadata.license !== "string" || !metadata.license.trim()
    ))
    .map(([path]) => path);

  assert.deepEqual(missing, []);
});

test("the local native module identifies the PlayAural license", async () => {
  const modulePackage = JSON.parse(await readFile(
    new URL(
      "../modules/playaural-spatial-audio/package.json",
      import.meta.url,
    ),
    "utf8",
  ));

  assert.equal(modulePackage.license, "GPL-2.0-only");
});
