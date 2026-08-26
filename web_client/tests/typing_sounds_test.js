import {
  DIGIT_SOUND_ASSETS,
  TYPING_DELETE_ASSET,
  TYPING_RETURN_ASSET,
  TYPING_SOUND_FAMILY,
  isImeCompositionKeyEvent,
  resolveTypingSoundCue,
} from "../typing_sounds.js";

const runButton = document.querySelector("#run");
const result = document.querySelector("#result");

function event(overrides = {}) {
  return {
    key: "",
    code: "",
    repeat: false,
    ctrlKey: false,
    altKey: false,
    metaKey: false,
    shiftKey: false,
    isComposing: false,
    ...overrides,
  };
}

function assertEqual(actual, expected, label) {
  if (JSON.stringify(actual) !== JSON.stringify(expected)) {
    throw new Error(
      `${label}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`,
    );
  }
}

runButton.addEventListener("click", () => {
  runButton.disabled = true;
  try {
    assertEqual(
      resolveTypingSoundCue(event({ key: "a", code: "KeyA" })),
      { family: TYPING_SOUND_FAMILY },
      "printable letter",
    );
    assertEqual(
      resolveTypingSoundCue(event({
        key: "Process",
        code: "KeyA",
        isComposing: true,
      })),
      { family: TYPING_SOUND_FAMILY },
      "IME physical letter",
    );
    assertEqual(
      resolveTypingSoundCue(event({
        key: "Process",
        code: "Digit5",
        isComposing: true,
      })),
      { asset: DIGIT_SOUND_ASSETS[5] },
      "IME physical digit",
    );
    assertEqual(
      resolveTypingSoundCue(event({ key: "5", code: "Numpad5" })),
      { asset: DIGIT_SOUND_ASSETS[5] },
      "numpad digit",
    );
    assertEqual(
      resolveTypingSoundCue(event({ key: "Backspace", ctrlKey: true })),
      { asset: TYPING_DELETE_ASSET },
      "word deletion",
    );
    assertEqual(
      resolveTypingSoundCue(event({ key: "Enter", isComposing: true })),
      { asset: TYPING_RETURN_ASSET },
      "IME candidate return",
    );
    assertEqual(
      resolveTypingSoundCue(event({ key: "a", code: "KeyA", repeat: true })),
      null,
      "held key",
    );
    assertEqual(
      resolveTypingSoundCue(event({ key: "a", code: "KeyA", ctrlKey: true })),
      null,
      "keyboard shortcut",
    );
    assertEqual(
      resolveTypingSoundCue(event({
        key: "@",
        code: "KeyQ",
        ctrlKey: true,
        altKey: true,
        getModifierState: (name) => name === "AltGraph",
      })),
      { family: TYPING_SOUND_FAMILY },
      "AltGraph text",
    );
    assertEqual(
      resolveTypingSoundCue(event({ key: "Process", isComposing: true })),
      null,
      "unidentifiable IME key",
    );
    assertEqual(
      isImeCompositionKeyEvent(event({ keyCode: 229 })),
      true,
      "IME boundary keyCode fallback",
    );

    const firstTelexPress = resolveTypingSoundCue(event({
      key: "Process",
      code: "KeyA",
      isComposing: true,
    }));
    const secondTelexPress = resolveTypingSoundCue(event({
      key: "Process",
      code: "KeyA",
      isComposing: true,
    }));
    assertEqual(
      [firstTelexPress, secondTelexPress],
      [
        { family: TYPING_SOUND_FAMILY },
        { family: TYPING_SOUND_FAMILY },
      ],
      "rapid Telex replacement sequence",
    );
    result.textContent = "PASS";
  } catch (error) {
    result.textContent = `FAIL: ${error.message}`;
  } finally {
    runButton.disabled = false;
  }
});
