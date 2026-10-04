import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import test from "node:test";
import ts from "typescript";

const sourceRoot = new URL("../src/", import.meta.url);
const bridgeUrl = new URL("../src/app/NativeTextInput.tsx", import.meta.url);
const inputSource = await readFile(
  bridgeUrl,
  "utf8",
);

async function findTsxFiles(directoryUrl) {
  const files = [];
  const entries = await readdir(directoryUrl, { withFileTypes: true });
  for (const entry of entries) {
    const entryUrl = new URL(entry.isDirectory() ? `${entry.name}/` : entry.name, directoryUrl);
    if (entry.isDirectory()) {
      files.push(...await findTsxFiles(entryUrl));
    } else if (entry.name.endsWith(".tsx")) {
      files.push(entryUrl);
    }
  }
  return files;
}

test("every application text field uses the shared native-editing bridge", async () => {
  const violations = [];
  for (const fileUrl of await findTsxFiles(sourceRoot)) {
    if (fileUrl.href === bridgeUrl.href) {
      continue;
    }

    const sourceText = await readFile(fileUrl, "utf8");
    const source = ts.createSourceFile(
      fileUrl.pathname,
      sourceText,
      ts.ScriptTarget.Latest,
      true,
      ts.ScriptKind.TSX,
    );
    const nativeTextInputNames = new Set();
    const reactNativeNamespaces = new Set();

    for (const statement of source.statements) {
      if (!ts.isImportDeclaration(statement) || statement.moduleSpecifier.text !== "react-native") {
        continue;
      }
      const importClause = statement.importClause;
      if (!importClause || importClause.isTypeOnly || !importClause.namedBindings) {
        continue;
      }
      if (ts.isNamespaceImport(importClause.namedBindings)) {
        reactNativeNamespaces.add(importClause.namedBindings.name.text);
        continue;
      }
      for (const element of importClause.namedBindings.elements) {
        if (!element.isTypeOnly && (element.propertyName?.text ?? element.name.text) === "TextInput") {
          nativeTextInputNames.add(element.name.text);
        }
      }
    }

    const visit = (node) => {
      if (ts.isJsxOpeningElement(node) || ts.isJsxSelfClosingElement(node)) {
        const tagName = node.tagName;
        const usesDirectImport = ts.isIdentifier(tagName) && nativeTextInputNames.has(tagName.text);
        const usesNamespaceImport = ts.isPropertyAccessExpression(tagName)
          && ts.isIdentifier(tagName.expression)
          && reactNativeNamespaces.has(tagName.expression.text)
          && tagName.name.text === "TextInput";
        if (usesDirectImport || usesNamespaceImport) {
          const position = source.getLineAndCharacterOfPosition(tagName.getStart(source));
          violations.push(`${fileUrl.pathname}:${position.line + 1}`);
        }
      }
      ts.forEachChild(node, visit);
    };
    visit(source);
  }

  assert.deepEqual(violations, []);
});

test("Android typing never writes an unchanged controlled value back to the native field", () => {
  assert.match(
    inputSource,
    /if \(Platform\.OS === "android"\) \{\s*nativeAndroidValueRef\.current = text;\s*\}\s*onChangeText\?\.\(text\);/u,
  );
  assert.match(
    inputSource,
    /Platform\.OS !== "android" \|\| nativeAndroidValueRef\.current === value/u,
  );
  assert.match(
    inputSource,
    /Platform\.OS === "android"\s*\? \{ defaultValue: initialAndroidValueRef\.current \}\s*: \{ value \}/u,
  );
});

test("intentional external value changes still update the Android native field", () => {
  assert.match(inputSource, /input\.setNativeProps\(\{ text: value \}\);/u);
  assert.match(inputSource, /Omit<TextInputProps, "defaultValue" \| "onChangeText" \| "value">/u);
});
