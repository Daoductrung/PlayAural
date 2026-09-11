import {
  HISTORY_BUFFER_ORDER,
  normalizeHistoryBuffer,
  normalizeMutedHistoryBuffers,
} from "../store.js";

export const HISTORY_COMPACT_MEDIA_QUERY = "(max-width: 920px), (pointer: coarse)";
export const HISTORY_TOUCH_MEDIA_QUERY = "(pointer: coarse)";

function getHistoryEntryText(entry) {
  if (typeof entry === "string") {
    return entry;
  }
  return typeof entry?.text === "string" ? entry.text : "";
}

export function createHistoryView({
  store,
  historyEl,
  historyLogEl,
  historyContentEl,
  historyToggleEl,
  bufferSelectEl,
  bufferMuteEl,
  a11y,
  announceFeedback = (text, options = {}) => a11y?.announce(text, options),
  initialMutedBuffers = [],
  onMutedBuffersChange = () => {},
  localize = (key, params = {}) => {
    let value = String(key || "");
    for (const [name, raw] of Object.entries(params || {})) {
      value = value.replaceAll(`{${name}}`, String(raw));
    }
    return value;
  },
  localizeBufferName = (name) => String(name || ""),
}) {
  const mutedBuffers = new Set();
  const bufferPositions = {};
  const usesTouchHistory = window.matchMedia(HISTORY_TOUCH_MEDIA_QUERY).matches;
  let historyCollapsed = window.matchMedia(HISTORY_COMPACT_MEDIA_QUERY).matches;
  let renderedLogBuffer = "";
  let renderedLogValue = "";
  let renderedLogRevision = -1;
  let renderScheduled = false;
  const bufferControlsEl = bufferSelectEl?.closest(".history-buffer-controls")
    || bufferSelectEl?.closest("label")
    || bufferSelectEl
    || null;

  setMutedBuffers(initialMutedBuffers, { notify: false });

  function ensureBufferPosition(bufferName) {
    if (!Object.hasOwn(bufferPositions, bufferName)) {
      bufferPositions[bufferName] = 0;
    }
  }

  function isBufferDirectlyMuted(bufferName) {
    return mutedBuffers.has(normalizeHistoryBuffer(bufferName));
  }

  function isBufferMuted(bufferName) {
    const name = normalizeHistoryBuffer(bufferName);
    return mutedBuffers.has("all") || mutedBuffers.has(name);
  }

  function getMutedBuffers() {
    return HISTORY_BUFFER_ORDER.filter((buffer) => mutedBuffers.has(buffer));
  }

  function setMutedBuffers(bufferNames, { notify = false } = {}) {
    const normalizedBuffers = normalizeMutedHistoryBuffers(bufferNames);
    const previouslyMuted = new Set(mutedBuffers);
    const changed = normalizedBuffers.length !== mutedBuffers.size
      || normalizedBuffers.some((buffer) => !mutedBuffers.has(buffer));
    mutedBuffers.clear();
    for (const bufferName of normalizedBuffers) {
      mutedBuffers.add(bufferName);
    }
    store.mergeHistoryIntoAll(
      [...previouslyMuted].filter((buffer) => !mutedBuffers.has(buffer)),
    );
    render();
    if (notify) {
      onMutedBuffersChange(getMutedBuffers());
    }
    return changed;
  }

  function getBufferNames() {
    return Object.keys(store.state.historyBuffers);
  }

  function getCurrentBufferName() {
    return store.state.historyBuffer || "all";
  }

  function getCurrentBufferLines() {
    const bufferName = getCurrentBufferName();
    return store.state.historyBuffers[bufferName] || [];
  }

  function clearHistory() {
    for (const name of getBufferNames()) {
      bufferPositions[name] = 0;
    }
    return store.clearHistory();
  }

  function getCurrentBufferInfo() {
    const name = getCurrentBufferName();
    const lines = getCurrentBufferLines();
    const position = Math.max(
      0,
      Math.min(Math.max(0, lines.length - 1), bufferPositions[name] || 0),
    );
    bufferPositions[name] = position;
    return {
      name,
      count: lines.length,
      position,
      muted: isBufferDirectlyMuted(name),
      effectivelyMuted: isBufferMuted(name),
    };
  }

  function announceBufferInfo() {
    const info = getCurrentBufferInfo();
    const status = info.effectivelyMuted ? localize("main-status-muted-suffix") : "";
    announceFeedback(localize("main-buffer-info", {
      name: localizeBufferName(info.name),
      status,
      count: info.count,
    }), { assertive: true, interrupt: true });
  }

  function getCurrentItemText() {
    const lines = getCurrentBufferLines();
    if (!lines.length) {
      return "";
    }
    const name = getCurrentBufferName();
    const position = Math.max(0, Math.min(lines.length - 1, bufferPositions[name] || 0));
    const index = lines.length - 1 - position;
    if (index < 0 || index >= lines.length) {
      return "";
    }
    return getHistoryEntryText(lines[index]);
  }

  function announceCurrentItem() {
    const bufferName = getCurrentBufferName();
    if (isBufferMuted(bufferName)) {
      announceFeedback(localize("history-buffer-muted-empty", {
        name: localizeBufferName(bufferName),
      }), { assertive: true, interrupt: true });
      return;
    }
    const text = getCurrentItemText();
    if (text) {
      announceFeedback(text, { assertive: true, interrupt: true });
    } else {
      announceFeedback(localize("main-buffer-empty"), { assertive: true, interrupt: true });
    }
  }

  function flushRender() {
    renderScheduled = false;
    for (const name of getBufferNames()) {
      ensureBufferPosition(name);
    }
    const bufferName = store.state.historyBuffer;
    const lines = isBufferMuted(bufferName) ? [] : (store.state.historyBuffers[bufferName] || []);
    if (bufferSelectEl && bufferSelectEl.value !== bufferName) {
      bufferSelectEl.value = bufferName;
    }
    renderBufferControls(bufferName);
    const joined = lines.map(getHistoryEntryText).join("\n");
    const revision = store.state.historyRevisions?.[bufferName] || 0;
    if (
      renderedLogBuffer === bufferName
      && renderedLogValue === joined
      && renderedLogRevision === revision
    ) {
      return;
    }
    renderedLogBuffer = bufferName;
    renderedLogValue = joined;
    renderedLogRevision = revision;

    historyEl.value = joined;

    if (historyLogEl) {
      const fragment = document.createDocumentFragment();
      for (const line of lines) {
        const row = document.createElement("p");
        row.className = "history-line";
        row.textContent = getHistoryEntryText(line);
        fragment.appendChild(row);
      }
      historyLogEl.replaceChildren(fragment);
    }
    scrollHistoryToLatest();
  }

  function render() {
    if (renderScheduled) {
      return;
    }
    renderScheduled = true;
    requestAnimationFrame(flushRender);
  }

  function scrollHistoryToLatest() {
    historyEl.scrollTop = historyEl.scrollHeight;
    if (historyLogEl) {
      historyLogEl.scrollTop = historyLogEl.scrollHeight;
    }
  }

  function scrollHistoryToLatestAfterLayout() {
    requestAnimationFrame(scrollHistoryToLatest);
  }

  function renderBufferControls(bufferName = getCurrentBufferName()) {
    if (bufferSelectEl) {
      for (const option of bufferSelectEl.options) {
        const name = normalizeHistoryBuffer(option.value);
        const localizedName = localize(`buffer-${name}`);
        option.textContent = isBufferMuted(name)
          ? localize("history-buffer-muted-name", { name: localizedName })
          : localizedName;
      }
    }
    if (!bufferMuteEl) {
      return;
    }
    const localizedName = localizeBufferName(bufferName);
    const mutedByAll = bufferName !== "all" && isBufferDirectlyMuted("all");
    const label = mutedByAll
      ? localize("history-buffer-muted-by-all", { name: localizedName })
      : localize(
        isBufferDirectlyMuted(bufferName) ? "history-buffer-unmute" : "history-buffer-mute",
        { name: localizedName },
      );
    bufferMuteEl.textContent = label;
    bufferMuteEl.setAttribute("aria-pressed", isBufferMuted(bufferName) ? "true" : "false");
  }

  function renderHistoryVisibility() {
    if (!historyContentEl || !historyToggleEl || !historyLogEl) {
      return;
    }
    if (bufferControlsEl) {
      bufferControlsEl.hidden = historyCollapsed;
    }
    if (
      historyCollapsed
      && (
        bufferControlsEl?.contains(document.activeElement)
        || historyContentEl.contains(document.activeElement)
      )
    ) {
      historyToggleEl.focus({ preventScroll: true });
    }
    historyToggleEl.hidden = false;
    historyToggleEl.tabIndex = 0;
    historyToggleEl.setAttribute("aria-expanded", historyCollapsed ? "false" : "true");
    historyContentEl.hidden = historyCollapsed;
    historyEl.hidden = usesTouchHistory;
    historyLogEl.setAttribute("aria-live", "off");
    historyLogEl.hidden = !usesTouchHistory;
    if (!historyCollapsed) {
      scrollHistoryToLatestAfterLayout();
    }
  }

  function addEntry(text, options = {}) {
    const {
      buffer = "misc",
      announce = true,
      assertive = false,
    } = options;

    const normalizedBuffer = normalizeHistoryBuffer(buffer);
    const incomingBufferMuted = isBufferMuted(normalizedBuffer);
    const sourceDirectlyMuted = normalizedBuffer !== "all" && isBufferDirectlyMuted(normalizedBuffer);
    store.addHistory(normalizedBuffer, text, { includeAll: !sourceDirectlyMuted });
    if (announce && !incomingBufferMuted) {
      a11y?.announce(text, { assertive });
    }
    return !incomingBufferMuted;
  }

  function switchBuffer({ step = 0, boundary = null } = {}) {
    const names = getBufferNames();
    if (!names.length) {
      return;
    }

    let nextIndex = Math.max(0, names.indexOf(getCurrentBufferName()));
    if (boundary === "first") {
      nextIndex = 0;
    } else if (boundary === "last") {
      nextIndex = names.length - 1;
    } else {
      nextIndex = Math.max(0, Math.min(names.length - 1, nextIndex + step));
    }
    store.setHistoryBuffer(names[nextIndex]);
    announceBufferInfo();
  }

  function moveInCurrentBuffer(direction) {
    const info = getCurrentBufferInfo();
    const maxPosition = Math.max(0, info.count - 1);
    let next = info.position;

    if (direction === "older") {
      next = Math.min(maxPosition, info.position + 1);
    } else if (direction === "newer") {
      next = Math.max(0, info.position - 1);
    } else if (direction === "oldest") {
      next = maxPosition;
    } else if (direction === "newest") {
      next = 0;
    }

    bufferPositions[info.name] = next;
    announceCurrentItem();
  }

  function toggleMuteCurrentBuffer() {
    const info = getCurrentBufferInfo();
    if (!info.name) {
      return false;
    }
    if (info.name !== "all" && isBufferDirectlyMuted("all")) {
      announceFeedback(localize("history-buffer-muted-by-all", {
        name: localizeBufferName(info.name),
      }), { assertive: true, interrupt: true });
      return false;
    }
    if (mutedBuffers.has(info.name)) {
      mutedBuffers.delete(info.name);
      store.mergeHistoryIntoAll([info.name]);
    } else {
      mutedBuffers.add(info.name);
    }
    render();
    onMutedBuffersChange(getMutedBuffers());
    const status = localize(mutedBuffers.has(info.name) ? "buffer-status-muted" : "buffer-status-unmuted");
    announceFeedback(localize("main-buffer-status", {
      name: localizeBufferName(info.name),
      status,
    }), { assertive: true, interrupt: true });
    return true;
  }

  if (bufferSelectEl) {
    bufferSelectEl.addEventListener("change", () => {
      store.setHistoryBuffer(bufferSelectEl.value);
      announceBufferInfo();
    });
  }
  if (bufferMuteEl) {
    bufferMuteEl.addEventListener("click", toggleMuteCurrentBuffer);
  }
  if (historyToggleEl) {
    historyToggleEl.addEventListener("click", () => {
      historyCollapsed = !historyCollapsed;
      renderHistoryVisibility();
    });
  }

  store.subscribe(render);
  renderHistoryVisibility();
  flushRender();

  return {
    addEntry,
    clearHistory,
    isBufferDirectlyMuted,
    isBufferMuted,
    getMutedBuffers,
    setMutedBuffers,
    render,
    previousBuffer() {
      switchBuffer({ step: -1 });
    },
    nextBuffer() {
      switchBuffer({ step: 1 });
    },
    firstBuffer() {
      switchBuffer({ boundary: "first" });
    },
    lastBuffer() {
      switchBuffer({ boundary: "last" });
    },
    olderMessage() {
      moveInCurrentBuffer("older");
    },
    newerMessage() {
      moveInCurrentBuffer("newer");
    },
    oldestMessage() {
      moveInCurrentBuffer("oldest");
    },
    newestMessage() {
      moveInCurrentBuffer("newest");
    },
    toggleCurrentBufferMute: toggleMuteCurrentBuffer,
    setCollapsed(collapsed) {
      historyCollapsed = Boolean(collapsed);
      renderHistoryVisibility();
    },
  };
}
