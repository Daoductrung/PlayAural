export async function copyTextToClipboard(
  text,
  {
    navigatorObject = globalThis.navigator,
    documentObject = globalThis.document,
  } = {},
) {
  if (typeof text !== "string" || text.length === 0) {
    return false;
  }

  try {
    const writeText = navigatorObject?.clipboard?.writeText;
    if (typeof writeText === "function") {
      await writeText.call(navigatorObject.clipboard, text);
      return true;
    }

    if (!documentObject?.body || typeof documentObject.createElement !== "function") {
      return false;
    }
    const textarea = documentObject.createElement("textarea");
    const previousFocus = documentObject.activeElement;
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.tabIndex = -1;
    textarea.style.position = "fixed";
    textarea.style.opacity = "0";
    textarea.style.pointerEvents = "none";
    documentObject.body.appendChild(textarea);
    try {
      textarea.focus();
      textarea.select();
      return documentObject.execCommand?.("copy") === true;
    } finally {
      try {
        if (typeof textarea.remove === "function") {
          textarea.remove();
        } else {
          documentObject.body.removeChild?.(textarea);
        }
      } catch {
        // Cleanup failures must not turn a successful clipboard write into a failure.
      }
      if (previousFocus && previousFocus !== textarea) {
        try {
          previousFocus.focus({ preventScroll: true });
        } catch {
          try {
            previousFocus.focus();
          } catch {
            // The prior element may have been removed during the operation.
          }
        }
      }
    }
  } catch {
    return false;
  }
}
