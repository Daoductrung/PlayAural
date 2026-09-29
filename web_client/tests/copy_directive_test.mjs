import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  COPY_DIRECTIVE_VERSION,
  MAX_COPY_FEEDBACK_LENGTH,
  MAX_COPY_TEXT_LENGTH,
  executeCopyDirective,
  validateCopyDirective,
} from "../copy_directive.js";

const conformance = JSON.parse(await readFile(
  new URL("../../copy_directive_conformance.json", import.meta.url),
  "utf8",
));

const validDirective = Object.freeze({
  version: 1,
  text: "first\nsecond",
  success_text: "Copied two entries.",
  failure_text: "Copy failed.",
});

test("copy directives validate and preserve the exact server payload", async () => {
  const writes = [];
  assert.deepEqual(validateCopyDirective(validDirective), validDirective);

  const result = await executeCopyDirective(
    validDirective,
    async (text) => { writes.push(text); return true; },
  );

  assert.deepEqual(writes, ["first\nsecond"]);
  assert.deepEqual(result, {
    accepted: true,
    copied: true,
    feedback: "Copied two entries.",
  });
});

test("copy directives fail closed on unexpected data and clipboard errors", async () => {
  const invalidValues = [
    null,
    [],
    { ...validDirective, version: true },
    { ...validDirective, version: 2 },
    { ...validDirective, text: "unsafe\u0000payload" },
    { ...validDirective, success_text: "Copied.\u202e" },
    { ...validDirective, unexpected: "field" },
  ];
  for (const value of invalidValues) {
    assert.equal(validateCopyDirective(value), null);
    assert.deepEqual(await executeCopyDirective(value, async () => true), {
      accepted: false,
      copied: false,
      feedback: "",
    });
  }

  assert.deepEqual(
    await executeCopyDirective(validDirective, async () => { throw new Error("denied"); }),
    { accepted: true, copied: false, feedback: "Copy failed." },
  );
});

test("copy directives match the shared protocol corpus and Unicode limits", () => {
  assert.equal(conformance.protocol_version, COPY_DIRECTIVE_VERSION);
  assert.deepEqual(conformance.limits, {
    text_code_points: MAX_COPY_TEXT_LENGTH,
    feedback_code_points: MAX_COPY_FEEDBACK_LENGTH,
  });
  for (const { name, directive } of conformance.valid) {
    assert.notEqual(validateCopyDirective(directive), null, name);
  }
  for (const { name, directive } of conformance.invalid) {
    assert.equal(validateCopyDirective(directive), null, name);
  }

  const common = {
    version: COPY_DIRECTIVE_VERSION,
    success_text: "Copied.",
    failure_text: "Failed.",
  };
  assert.notEqual(
    validateCopyDirective({ ...common, text: "😀".repeat(MAX_COPY_TEXT_LENGTH) }),
    null,
  );
  assert.equal(
    validateCopyDirective({ ...common, text: "x".repeat(MAX_COPY_TEXT_LENGTH + 1) }),
    null,
  );
  assert.equal(
    validateCopyDirective({ ...common, text: "bad\uD800value" }),
    null,
  );
  assert.equal(validateCopyDirective({ ...common, text: "bad\uD800" }), null);
  const hostile = new Proxy(validDirective, {
    ownKeys() { throw new Error("unexpected object behavior"); },
  });
  assert.equal(validateCopyDirective(hostile), null);
});
