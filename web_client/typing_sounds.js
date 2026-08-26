export const TYPING_SOUND_FAMILY = "typing";
export const TYPING_SOUND_HANDLE = "client:typing-feedback";
export const TYPING_SOUND_VOLUME = 50;

const DIGIT_NAMES = Object.freeze([
  "zero",
  "one",
  "two",
  "three",
  "four",
  "five",
  "six",
  "seven",
  "eight",
  "nine",
]);

export const DIGIT_SOUND_ASSETS = Object.freeze(
  DIGIT_NAMES.map((name) => `typing_digit_${name}.ogg`),
);
export const TYPING_DELETE_ASSET = "typing_delete.ogg";
export const TYPING_RETURN_ASSET = "typing_return.ogg";
export const TYPING_EXACT_ASSETS = Object.freeze([
  ...DIGIT_SOUND_ASSETS,
  TYPING_DELETE_ASSET,
  TYPING_RETURN_ASSET,
]);

const DELETE_KEYS = new Set(["Backspace", "Delete"]);
const RETURN_KEYS = new Set(["Enter", "NumpadEnter"]);
const GENERIC_PHYSICAL_CODES = new Set([
  "Space",
  "Backquote",
  "Minus",
  "Equal",
  "BracketLeft",
  "BracketRight",
  "Backslash",
  "Semicolon",
  "Quote",
  "Comma",
  "Period",
  "Slash",
  "IntlBackslash",
  "IntlRo",
  "IntlYen",
  "NumpadDecimal",
  "NumpadAdd",
  "NumpadSubtract",
  "NumpadMultiply",
  "NumpadDivide",
]);

function digitFromEvent(key, code) {
  if (/^[0-9]$/.test(key)) {
    return Number(key);
  }
  const match = /^(?:Digit|Numpad)([0-9])$/.exec(code);
  return match ? Number(match[1]) : null;
}

function isPhysicalTextCode(code) {
  return /^Key[A-Z]$/.test(code) || GENERIC_PHYSICAL_CODES.has(code);
}

export function isImeCompositionKeyEvent(event) {
  return Boolean(event?.isComposing || event?.keyCode === 229);
}

export function resolveTypingSoundCue(event) {
  if (!event || event.repeat === true) {
    return null;
  }

  const key = String(event.key || "");
  const code = String(event.code || "");
  if (DELETE_KEYS.has(key) || code === "Backspace" || code === "Delete") {
    return { asset: TYPING_DELETE_ASSET };
  }
  if (RETURN_KEYS.has(key) || RETURN_KEYS.has(code)) {
    return { asset: TYPING_RETURN_ASSET };
  }
  const altGraph = event.getModifierState?.("AltGraph") === true;
  if (event.metaKey || ((event.ctrlKey || event.altKey) && !altGraph)) {
    return null;
  }

  const digit = digitFromEvent(key, code);
  if (digit !== null) {
    return { asset: DIGIT_SOUND_ASSETS[digit] };
  }
  if (
    (key.length === 1 && key.codePointAt(0) >= 32)
    || isPhysicalTextCode(code)
  ) {
    return { family: TYPING_SOUND_FAMILY };
  }
  return null;
}
