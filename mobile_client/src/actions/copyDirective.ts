import * as Clipboard from "expo-clipboard";

import type { CopyDirectiveData } from "../network/packets";

export const COPY_DIRECTIVE_VERSION = 1;
export const MAX_COPY_TEXT_LENGTH = 131_072;
export const MAX_COPY_FEEDBACK_LENGTH = 1_000;

const COPY_DIRECTIVE_FIELDS = Object.freeze([
  "failure_text",
  "success_text",
  "text",
  "version",
]);
const UNSAFE_COPY_CONTROL = /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F-\u009F\u061C\u200E\u200F\u2028\u2029\u202A-\u202E\u2066-\u206F]/u;
const UNSAFE_FEEDBACK_CONTROL = /[\u0000-\u001F\u007F-\u009F\u061C\u200E\u200F\u2028\u2029\u202A-\u202E\u2066-\u206F]/u;

function exceedsUnicodeLength(value: string, maximum: number): boolean {
  let length = 0;
  for (const _character of value) {
    length += 1;
    if (length > maximum) {
      return true;
    }
  }
  return false;
}

function hasUnpairedSurrogate(value: string): boolean {
  for (let index = 0; index < value.length; index += 1) {
    const code = value.charCodeAt(index);
    if (code >= 0xD800 && code <= 0xDBFF) {
      const next = value.charCodeAt(index + 1);
      if (!(next >= 0xDC00 && next <= 0xDFFF)) {
        return true;
      }
      index += 1;
    } else if (code >= 0xDC00 && code <= 0xDFFF) {
      return true;
    }
  }
  return false;
}

export type CopyExecutionResult = Readonly<{
  accepted: boolean;
  copied: boolean;
  feedback: string;
}>;

export function validateCopyDirective(value: unknown): CopyDirectiveData | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  try {
    const candidate = value as Record<string, unknown>;
    const fields = Object.keys(candidate).sort();
    if (
      fields.length !== COPY_DIRECTIVE_FIELDS.length
      || fields.some((field, index) => field !== COPY_DIRECTIVE_FIELDS[index])
      || !Number.isInteger(candidate.version)
      || candidate.version !== COPY_DIRECTIVE_VERSION
      || typeof candidate.text !== "string"
      || candidate.text.length === 0
      || exceedsUnicodeLength(candidate.text, MAX_COPY_TEXT_LENGTH)
      || hasUnpairedSurrogate(candidate.text)
      || UNSAFE_COPY_CONTROL.test(candidate.text)
      || typeof candidate.success_text !== "string"
      || !candidate.success_text.trim()
      || exceedsUnicodeLength(candidate.success_text, MAX_COPY_FEEDBACK_LENGTH)
      || hasUnpairedSurrogate(candidate.success_text)
      || UNSAFE_FEEDBACK_CONTROL.test(candidate.success_text)
      || typeof candidate.failure_text !== "string"
      || !candidate.failure_text.trim()
      || exceedsUnicodeLength(candidate.failure_text, MAX_COPY_FEEDBACK_LENGTH)
      || hasUnpairedSurrogate(candidate.failure_text)
      || UNSAFE_FEEDBACK_CONTROL.test(candidate.failure_text)
    ) {
      return null;
    }
    return Object.freeze({
      version: COPY_DIRECTIVE_VERSION,
      text: candidate.text,
      success_text: candidate.success_text,
      failure_text: candidate.failure_text,
    });
  } catch {
    return null;
  }
}

export async function executeCopyDirective(
  value: unknown,
  copyText: (text: string) => Promise<boolean> = Clipboard.setStringAsync,
): Promise<CopyExecutionResult> {
  const directive = validateCopyDirective(value);
  if (!directive) {
    return Object.freeze({ accepted: false, copied: false, feedback: "" });
  }
  let copied = false;
  try {
    copied = await copyText(directive.text) === true;
  } catch {
    copied = false;
  }
  return Object.freeze({
    accepted: true,
    copied,
    feedback: copied ? directive.success_text : directive.failure_text,
  });
}
