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
  assert.equal(lock.packages[""].license, "GPL-3.0-or-later");
});

test("PlayAural packages identify the project license", async () => {
  const [rootPackage, modulePackage] = await Promise.all([
    readFile(new URL("../package.json", import.meta.url), "utf8"),
    readFile(
      new URL(
        "../modules/playaural-spatial-audio/package.json",
        import.meta.url,
      ),
      "utf8",
    ),
  ]).then((contents) => contents.map((content) => JSON.parse(content)));

  assert.equal(rootPackage.license, "GPL-3.0-or-later");
  assert.equal(modulePackage.license, "GPL-3.0-or-later");
});
