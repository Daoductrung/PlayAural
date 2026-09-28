import { copyTextToClipboard } from "./clipboard.js";

export const COPY_DIRECTIVE_VERSION = 1;
export const MAX_COPY_TEXT_LENGTH = 131072;
export const MAX_COPY_FEEDBACK_LENGTH = 1000;

const COPY_DIRECTIVE_FIELDS = Object.freeze([
  "failure_text",
  "success_text",
  "text",
  "version",
]);
const UNSAFE_COPY_CONTROL = /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F-\u009F\u061C\u200E\u200F\u2028\u2029\u202A-\u202E\u2066-\u206F]/u;
const UNSAFE_FEEDBACK_CONTROL = /[\u0000-\u001F\u007F-\u009F\u061C\u200E\u200F\u2028\u2029\u202A-\u202E\u2066-\u206F]/u;

function exceedsUnicodeLength(value, maximum) {
  let length = 0;
  for (const _character of value) {
    length += 1;
    if (length > maximum) {
      return true;
    }
  }
  return false;
}

function hasUnpairedSurrogate(value) {
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

export function validateCopyDirective(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return null;
  }
  try {
    const fields = Object.keys(value).sort();
    if (
      fields.length !== COPY_DIRECTIVE_FIELDS.length
      || fields.some((field, index) => field !== COPY_DIRECTIVE_FIELDS[index])
      || !Number.isInteger(value.version)
      || value.version !== COPY_DIRECTIVE_VERSION
      || typeof value.text !== "string"
      || value.text.length === 0
      || exceedsUnicodeLength(value.text, MAX_COPY_TEXT_LENGTH)
      || hasUnpairedSurrogate(value.text)
      || UNSAFE_COPY_CONTROL.test(value.text)
      || typeof value.success_text !== "string"
      || !value.success_text.trim()
      || exceedsUnicodeLength(value.success_text, MAX_COPY_FEEDBACK_LENGTH)
      || hasUnpairedSurrogate(value.success_text)
      || UNSAFE_FEEDBACK_CONTROL.test(value.success_text)
      || typeof value.failure_text !== "string"
      || !value.failure_text.trim()
      || exceedsUnicodeLength(value.failure_text, MAX_COPY_FEEDBACK_LENGTH)
      || hasUnpairedSurrogate(value.failure_text)
      || UNSAFE_FEEDBACK_CONTROL.test(value.failure_text)
    ) {
      return null;
    }
    return Object.freeze({
      version: value.version,
      text: value.text,
      success_text: value.success_text,
      failure_text: value.failure_text,
    });
  } catch {
    return null;
  }
}

export async function executeCopyDirective(
  value,
  copyText = copyTextToClipboard,
) {
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
