import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

test("Android prebuild installs the reviewed board viewport under the configured package", () => {
  const plugin = new URL("../plugins/withPlayAuralBackgroundService.js", import.meta.url);
  const written = new Map();
  const module = { exports: {} };
  new Function("require", "module", "__dirname", fs.readFileSync(plugin, "utf8") + "\nmodule.exports = withPlayAuralNativeFiles;")(
    (id) => id === "fs" ? { ...fs, mkdirSync() {}, writeFileSync: (target, source) => written.set(path.basename(target), source) }
      : id === "path" ? path : { withDangerousMod: (config, [platform, apply]) => {
        assert.equal(platform, "android"); return apply(config);
      } },
    module, path.dirname(fileURLToPath(plugin)),
  );
  module.exports({ android: { package: "test.review.board" }, modRequest: { platformProjectRoot: "unused" } });
  const reviewed = fs.readFileSync(new URL("../native/android/BoardViewportManager.kt", import.meta.url), "utf8");
  assert.equal(written.get("BoardViewportManager.kt"), reviewed.replace("__PLAYAURAL_PACKAGE__", "test.review.board"));
  assert.match(written.get("PlayAuralNativePackage.kt"), /listOf\(BoardViewportManager\(\)\)/);
  assert.equal(written.get("BoardViewportManager.kt").includes("__PLAYAURAL_PACKAGE__"), false);
});
