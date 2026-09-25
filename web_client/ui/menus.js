export function isMenuItemActionable(item) {
  return typeof item?.id === "string" && item.id.length > 0 && item.read_only !== true;
}

function normalizeForSearch(value) {
  const text = String(value || "")
    .replace(/\u0111/g, "d")
    .replace(/\u0110/g, "D");
  return text
    .normalize("NFD")
    .replace(/\p{Mark}/gu, "")
    .toLowerCase();
}

export function createMenuView({
  store,
  listEl,
  onActivate,
  onSelectionSound,
  onActivateSound,
  onBoundaryRepeat,
  onContextAction,
  getDefaultLabel = () => "Game menu",
}) {
  let renderVersion = 0;
  let lastStructureSnapshot = "";
  let lastSelection = -1;
  const isCoarsePointer = window.matchMedia("(pointer: coarse)").matches;
  const useActiveDescendant = !isCoarsePointer;
  let searchBuffer = "";
  let lastTypeTime = 0;
  const typeTimeoutSeconds = 0.15;
  const longPressTimers = new WeakMap();
  const touchPointers = new WeakMap();
  let suppressClickUntil = 0;

  function menuStructureSnapshot(menu) {
    const itemsSnapshot = (menu.items || [])
      .map((item) => `${item?.id ?? ""}|${item?.text ?? ""}|${item?.sound ?? ""}|${item?.read_only === true ? "1" : "0"}`)
      .join("||");
    return [
      menu.menuId ?? "",
      menu.title ?? "",
      menu.multiletterEnabled ? "1" : "0",
      menu.escapeBehavior ?? "",
      menu.gridEnabled ? "1" : "0",
      menu.gridWidth ?? 1,
      itemsSnapshot,
    ].join("::");
  }

  function currentOptionId(index) {
    return `menu-option-${renderVersion}-${index}`;
  }

  function itemAt(index) {
    return store.state.currentMenu.items[index] || null;
  }

  function setSelection(next, { playSound = true } = {}) {
    const count = store.state.currentMenu.items.length;
    if (!count) {
      store.setMenu({ selection: 0 });
      return;
    }
    const bounded = Math.max(0, Math.min(count - 1, next));
    if (bounded === store.state.currentMenu.selection) {
      return;
    }
    store.setMenu({ selection: bounded });
    if (playSound && onSelectionSound) {
      onSelectionSound(itemAt(bounded), bounded);
    }
  }

  function moveSelection(delta) {
    const menu = store.state.currentMenu;
    const count = menu.items.length;
    if (!count) {
      return;
    }
    const current = menu.selection;
    const bounded = Math.max(0, Math.min(count - 1, current + delta));
    if (bounded === current) {
      if (onSelectionSound) {
        onSelectionSound(menu.items[current], current);
      }
      const currentItem = menu.items[current];
      if (currentItem && onBoundaryRepeat) {
        onBoundaryRepeat(currentItem.text);
      }
      return;
    }
    setSelection(bounded);
  }

  function moveGrid(direction) {
    const menu = store.state.currentMenu;
    if (!menu.gridEnabled || menu.gridWidth <= 1 || !menu.items.length) {
      moveSelection(direction === "left" || direction === "up" ? -1 : 1);
      return;
    }
    const width = Math.max(1, Number(menu.gridWidth) || 1);
    const current = menu.selection;
    let next = current;
    if (direction === "left" && current % width > 0) {
      next = current - 1;
    } else if (direction === "right" && current % width < width - 1 && current + 1 < menu.items.length) {
      next = current + 1;
    } else if (direction === "up" && current - width >= 0) {
      next = current - width;
    } else if (direction === "down" && current + width < menu.items.length) {
      next = current + width;
    }
    if (next === current) {
      const currentItem = menu.items[current];
      if (currentItem && onBoundaryRepeat) {
        onBoundaryRepeat(currentItem.text);
      }
      if (onSelectionSound) {
        onSelectionSound(currentItem, current);
      }
      return;
    }
    setSelection(next);
  }

  function handleTypeNavigation(char) {
    const menu = store.state.currentMenu;
    const count = menu.items.length;
    if (!count || !char) {
      return;
    }

    const now = performance.now() / 1000;
    if (now - lastTypeTime > typeTimeoutSeconds) {
      searchBuffer = "";
    }
    searchBuffer += char.toLowerCase();
    lastTypeTime = now;

    const search = normalizeForSearch(searchBuffer);
    const current = menu.selection;
    const currentItem = menu.items[current];
    const currentText = normalizeForSearch(currentItem?.text || "");

    if (searchBuffer.length > 1 && currentText.startsWith(search)) {
      return;
    }

    const start = current >= 0 ? current : 0;
    for (let offset = 1; offset <= count; offset += 1) {
      const i = (start + offset) % count;
      const text = normalizeForSearch(menu.items[i]?.text || "");
      if (text.startsWith(search)) {
        setSelection(i);
        return;
      }
    }
  }

  function activateSelection() {
    const menu = store.state.currentMenu;
    if (!menu.items.length) {
      return;
    }
    const item = menu.items[menu.selection];
    if (!item) {
      return;
    }
    if (!isMenuItemActionable(item)) {
      return;
    }
    if (onActivateSound) {
      onActivateSound();
    }
    onActivate(item, menu.selection);
  }

  function activateIndex(index) {
    const item = itemAt(index);
    if (!item) {
      return;
    }
    setSelection(index, { playSound: false });
    if (!isMenuItemActionable(item)) {
      return;
    }
    if (onActivateSound) {
      onActivateSound();
    }
    onActivate(item, index);
  }

  function focusSelection() {
    const menu = store.state.currentMenu;
    if (!menu.items.length) {
      listEl.focus({ preventScroll: true });
      return;
    }
    if (isCoarsePointer) {
      const index = Math.max(0, Math.min(menu.selection, menu.items.length - 1));
      const button = listEl.children[index]?.querySelector("button");
      if (button) {
        button.focus({ preventScroll: true });
        return;
      }
    }
    listEl.focus({ preventScroll: true });
  }

  function contextAction(index) {
    const item = itemAt(index);
    if (!isMenuItemActionable(item)) {
      return;
    }
    setSelection(index, { playSound: false });
    onContextAction?.(item, index);
  }

  function installContextHandlers(target, index) {
    target.addEventListener("contextmenu", (event) => {
      event.preventDefault();
      contextAction(index);
    });
    target.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && event.shiftKey) {
        event.preventDefault();
        event.stopPropagation();
        contextAction(index);
      }
    });
    target.addEventListener("pointerdown", (event) => {
      if (event.pointerType === "mouse" && event.button !== 0) {
        return;
      }
      delete target.dataset.longPressContext;
      const timer = window.setTimeout(() => {
        longPressTimers.delete(target);
        target.dataset.longPressContext = "1";
        contextAction(index);
        if (navigator.vibrate) {
          navigator.vibrate(35);
        }
      }, 800);
      longPressTimers.set(target, timer);
    });
    const cancel = () => {
      const timer = longPressTimers.get(target);
      if (timer) {
        window.clearTimeout(timer);
        longPressTimers.delete(target);
      }
    };
    target.addEventListener("pointerup", cancel);
    target.addEventListener("pointercancel", cancel);
    target.addEventListener("pointerleave", cancel);
    target.addEventListener("pointermove", cancel);
  }

  function applySelection(selectionIndex) {
    const menu = store.state.currentMenu;
    const boundedSelection = menu.items.length
      ? Math.max(0, Math.min(menu.items.length - 1, selectionIndex))
      : 0;
    const children = listEl.children;
    for (let i = 0; i < children.length; i += 1) {
      const li = children[i];
      const active = i === boundedSelection;
      if (!isCoarsePointer) {
        li.setAttribute("aria-selected", active ? "true" : "false");
      }
      li.classList.toggle("active", active);
    }
    const activeEl = children[boundedSelection];
    if (activeEl) {
      activeEl.scrollIntoView({ block: "nearest", inline: "nearest" });
    }
    if (useActiveDescendant && menu.items.length > 0) {
      listEl.setAttribute("aria-activedescendant", currentOptionId(boundedSelection));
    } else {
      listEl.removeAttribute("aria-activedescendant");
    }
    lastSelection = boundedSelection;
  }

  function renderFull() {
    const menu = store.state.currentMenu;
    renderVersion += 1;
    searchBuffer = "";
    lastTypeTime = 0;
    listEl.replaceChildren();
    listEl.classList.toggle("grid-mode", Boolean(menu.gridEnabled && menu.gridWidth > 1));
    listEl.style.setProperty("--grid-cols", String(Math.max(1, Number(menu.gridWidth) || 1)));
    if (menu.title) {
      listEl.setAttribute("aria-label", menu.title);
    } else {
      listEl.setAttribute("aria-label", getDefaultLabel());
    }
    if (isCoarsePointer) {
      listEl.removeAttribute("role");
    } else {
      listEl.setAttribute("role", "listbox");
    }

    menu.items.forEach((item, index) => {
      const actionable = isMenuItemActionable(item);
      const li = document.createElement("li");
      li.id = currentOptionId(index);
      li.className = "menu-item";
      li.dataset.index = String(index);
      if (item?.id !== null && item?.id !== undefined) {
        li.dataset.itemId = String(item.id);
      }
      if (item?.sound) {
        li.dataset.sound = item.sound;
      }
      li.setAttribute("aria-disabled", actionable ? "false" : "true");

      if (isCoarsePointer) {
        li.setAttribute("role", "presentation");
        const button = document.createElement("button");
        button.type = "button";
        button.className = "menu-item-touch";
        button.textContent = item.text;
        button.setAttribute("aria-disabled", actionable ? "false" : "true");
        button.addEventListener("focus", () => {
          setSelection(index);
        });
        button.addEventListener("pointerdown", (event) => {
          if (event.pointerType === "mouse" && event.button !== 0) {
            return;
          }
          touchPointers.set(button, {
            id: event.pointerId,
            x: event.clientX,
            y: event.clientY,
            cancelled: false,
          });
        }, { passive: true });
        button.addEventListener("pointermove", (event) => {
          const pointer = touchPointers.get(button);
          if (!pointer || pointer.id !== event.pointerId) {
            return;
          }
          if (Math.abs(event.clientX - pointer.x) > 12 || Math.abs(event.clientY - pointer.y) > 12) {
            pointer.cancelled = true;
          }
        }, { passive: true });
        button.addEventListener("pointercancel", () => {
          touchPointers.delete(button);
        });
        button.addEventListener("pointerup", (event) => {
          const pointer = touchPointers.get(button);
          touchPointers.delete(button);
          if (button.dataset.longPressContext === "1") {
            delete button.dataset.longPressContext;
            return;
          }
          if (!pointer || pointer.id !== event.pointerId || pointer.cancelled) {
            return;
          }
          if (event.cancelable) {
            event.preventDefault();
          }
          suppressClickUntil = performance.now() + 750;
          activateIndex(index);
        });
        button.addEventListener("click", () => {
          if (performance.now() < suppressClickUntil) {
            return;
          }
          activateIndex(index);
        });
        installContextHandlers(button, index);
        li.appendChild(button);
      } else {
        li.setAttribute("role", "option");
        li.textContent = item.text;
        li.addEventListener("click", () => {
          const wasSelected = index === store.state.currentMenu.selection;
          setSelection(index);
          if (wasSelected && actionable) {
            activateSelection();
          }
        });
        li.addEventListener("dblclick", () => {
          setSelection(index);
          if (actionable) {
            activateSelection();
          }
        });
        installContextHandlers(li, index);
      }
      listEl.appendChild(li);
    });
    applySelection(menu.selection);
  }

  listEl.addEventListener("focus", () => {
    applySelection(store.state.currentMenu.selection);
  });

  store.subscribe(() => {
    const menu = store.state.currentMenu;
    const nextStructureSnapshot = menuStructureSnapshot(menu);
    if (nextStructureSnapshot !== lastStructureSnapshot) {
      lastStructureSnapshot = nextStructureSnapshot;
      renderFull();
      return;
    }
    if (menu.selection !== lastSelection) {
      applySelection(menu.selection);
    }
  });
  lastStructureSnapshot = menuStructureSnapshot(store.state.currentMenu);
  renderFull();

  return {
    setSelection,
    moveSelection,
    moveGrid,
    handleTypeNavigation,
    activateSelection,
    focusSelection,
    getElement() {
      return listEl;
    },
    getCurrentItemText() {
      const menu = store.state.currentMenu;
      if (!menu.items.length) {
        return "";
      }
      const currentItem = menu.items[Math.max(0, Math.min(menu.selection, menu.items.length - 1))];
      return currentItem?.text || "";
    },
  };
}
