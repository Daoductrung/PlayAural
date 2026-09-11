function keyFromEvent(event) {
  if (event.key === " ") {
    return "space";
  }
  if (event.key === "Escape") {
    return "escape";
  }
  if (event.key === "Backspace") {
    return "backspace";
  }
  if (event.key === "Enter") {
    return "enter";
  }
  if (event.key.startsWith("F") && /^F\d+$/.test(event.key)) {
    return event.key.toLowerCase();
  }

  const lower = event.key.toLowerCase();
  if (/^[a-z0-9]$/.test(lower)) {
    return lower;
  }
  if (["arrowup", "arrowdown", "arrowleft", "arrowright"].includes(lower)) {
    return lower.replace("arrow", "");
  }
  return null;
}

function isTypingTarget(element) {
  if (!element) {
    return false;
  }
  const tag = element.tagName;
  return tag === "INPUT" || tag === "TEXTAREA" || element.isContentEditable;
}

function isEditableTarget(element) {
  if (!isTypingTarget(element)) {
    return false;
  }
  if (element.disabled) {
    return false;
  }
  if (element.readOnly) {
    return false;
  }
  return true;
}

export function installKeybinds({
  store,
  menuView,
  sendMenuSelection,
  sendEscape,
  sendKeybind,
  sendListOnline,
  sendListOnlineWithGames,
  onFocusMenu,
  onFocusChat,
  onToggleVoiceChat,
  onToggleVoiceMic,
  onFocusHistory,
  onOpenFriends,
  onOpenAdmin,
  onOpenOptions,
  onPreviousBuffer,
  onNextBuffer,
  onFirstBuffer,
  onLastBuffer,
  onOlderMessage,
  onNewerMessage,
  onOldestMessage,
  onNewestMessage,
  onToggleBufferMute,
  onToggleTableChat,
  onToggleGlobalChat,
  onAmbienceDown,
  onAmbienceUp,
  onMusicDown,
  onMusicUp,
  onPing,
  isModalOpen,
}) {
  document.addEventListener("keydown", (event) => {
    if (isModalOpen && isModalOpen()) {
      return;
    }

    const menu = store.state.currentMenu;
    const activeElement = document.activeElement;
    const typing = isTypingTarget(activeElement);
    const editing = isEditableTarget(activeElement);
    const menuElement = menuView.getElement();
    const menuFocused = activeElement === menuElement || Boolean(menuElement?.contains(activeElement));
    const connected = store.state.connection.authenticated;

    if (
      connected
      && event.altKey
      && event.shiftKey
      && !event.ctrlKey
      && !event.metaKey
      && event.key.toLowerCase() === "v"
    ) {
      event.preventDefault();
      onToggleVoiceMic?.();
      return;
    }

    if (
      connected
      && event.altKey
      && event.shiftKey
      && !event.ctrlKey
      && !event.metaKey
      && event.key.toLowerCase() === "a"
    ) {
      event.preventDefault();
      onOpenAdmin?.();
      return;
    }

    if (
      connected
      && event.altKey
      && !event.ctrlKey
      && !event.shiftKey
      && !event.metaKey
    ) {
      const altKey = event.key.toLowerCase();
      if (altKey === "m") {
        event.preventDefault();
        onFocusMenu?.();
        return;
      }
      if (altKey === "c") {
        event.preventDefault();
        onFocusChat?.();
        return;
      }
      if (altKey === "v") {
        event.preventDefault();
        onToggleVoiceChat?.();
        return;
      }
      if (altKey === "h") {
        event.preventDefault();
        onFocusHistory?.();
        return;
      }
      if (altKey === "p") {
        event.preventDefault();
        onPing?.();
        return;
      }
      if (altKey === "f") {
        event.preventDefault();
        onOpenFriends?.();
        return;
      }
      if (altKey === "o") {
        event.preventDefault();
        onOpenOptions?.();
        return;
      }
    }

    if (
      connected
      && event.key === "F1"
      && event.ctrlKey
      && !event.altKey
      && !event.shiftKey
      && !event.metaKey
    ) {
      event.preventDefault();
      sendKeybind({
        key: "f1",
        control: true,
        alt: false,
        shift: false,
        menu_id: menu.menuId,
        menu_index: menu.items.length ? menu.selection + 1 : null,
        menu_item_id: menu.items[menu.selection]?.id ?? null,
      });
      return;
    }

    if (event.key === "Backspace" && !editing) {
      // Avoid browser navigation/context behavior outside editable controls.
      event.preventDefault();
      if (!menuFocused) {
        return;
      }
    }

    if (connected && !event.altKey && !event.ctrlKey && !event.metaKey) {
      if (event.key === "F2") {
        event.preventDefault();
        if (event.shiftKey) {
          sendListOnlineWithGames?.();
        } else {
          sendListOnline?.();
        }
        return;
      }
      if (event.key === "F1" && !event.shiftKey) {
        event.preventDefault();
        onPing?.();
        return;
      }
      if (menuFocused && event.key === "F4" && !event.shiftKey) {
        event.preventDefault();
        onToggleBufferMute?.();
        return;
      }
      if (event.key === "F6") {
        event.preventDefault();
        if (event.shiftKey) {
          onToggleGlobalChat?.();
        } else {
          onToggleTableChat?.();
        }
        return;
      }
      if (event.key === "F7" && !event.shiftKey) {
        event.preventDefault();
        onAmbienceDown?.();
        return;
      }
      if (event.key === "F8" && !event.shiftKey) {
        event.preventDefault();
        onAmbienceUp?.();
        return;
      }
      if (event.key === "F9" && !event.shiftKey) {
        event.preventDefault();
        onMusicDown?.();
        return;
      }
      if (event.key === "F10" && !event.shiftKey) {
        event.preventDefault();
        onMusicUp?.();
        return;
      }
    }

    if (
      connected
      && (event.key === "w" || event.key === "W")
      && event.ctrlKey
      && !event.altKey
      && !event.metaKey
    ) {
      event.preventDefault();
      const menuIndex = menu.items.length ? menu.selection + 1 : null;
      const currentItem = menu.items[menu.selection] || null;
      sendKeybind({
        key: "w",
        control: true,
        alt: false,
        shift: event.shiftKey,
        menu_id: menu.menuId,
        menu_index: menuIndex,
        menu_item_id: currentItem?.id ?? null,
      });
      return;
    }

    if (menuFocused) {
      // Alt+Arrow: jump to grid row/column edges
      if (event.altKey && !event.ctrlKey && !event.metaKey && menu.gridEnabled && menu.gridWidth > 1) {
        const width = menu.gridWidth;
        const count = menu.items.length;
        const current = menu.selection;
        const row = Math.floor(current / width);
        const col = current % width;

        if (event.key === "ArrowLeft") {
          event.preventDefault();
          menuView.setSelection(row * width);
          return;
        }
        if (event.key === "ArrowRight") {
          event.preventDefault();
          menuView.setSelection(Math.min((row + 1) * width - 1, count - 1));
          return;
        }
        if (event.key === "ArrowUp") {
          event.preventDefault();
          menuView.setSelection(col);
          return;
        }
        if (event.key === "ArrowDown") {
          event.preventDefault();
          let bottom = col;
          while (bottom + width < count) {
            bottom += width;
          }
          menuView.setSelection(bottom);
          return;
        }
      }

      // Plain arrows move locally; modified arrows fall through to server keybinds.
      if (!event.ctrlKey && !event.altKey && !event.shiftKey && !event.metaKey) {
        if (event.key === "ArrowUp") {
          event.preventDefault();
          menu.gridEnabled ? menuView.moveGrid("up") : menuView.moveSelection(-1);
          return;
        }
        if (event.key === "ArrowLeft") {
          event.preventDefault();
          menu.gridEnabled ? menuView.moveGrid("left") : menuView.moveSelection(-1);
          return;
        }
        if (event.key === "ArrowDown") {
          event.preventDefault();
          menu.gridEnabled ? menuView.moveGrid("down") : menuView.moveSelection(1);
          return;
        }
        if (event.key === "ArrowRight") {
          event.preventDefault();
          menu.gridEnabled ? menuView.moveGrid("right") : menuView.moveSelection(1);
          return;
        }
      }
      if (event.key === "Home") {
        event.preventDefault();
        if (menu.gridEnabled && menu.gridWidth > 1) {
          const row = Math.floor(menu.selection / menu.gridWidth);
          menuView.setSelection(row * menu.gridWidth);
        } else {
          menuView.setSelection(0);
        }
        return;
      }
      if (event.key === "End") {
        event.preventDefault();
        if (menu.gridEnabled && menu.gridWidth > 1) {
          const row = Math.floor(menu.selection / menu.gridWidth);
          menuView.setSelection(Math.min((row + 1) * menu.gridWidth - 1, menu.items.length - 1));
        } else {
          menuView.setSelection(Math.max(0, menu.items.length - 1));
        }
        return;
      }
      if (event.key === "Enter" && !event.altKey && !event.ctrlKey && !event.shiftKey) {
        event.preventDefault();
        menuView.activateSelection();
        return;
      }

      const typedChar = event.key.length === 1 ? event.key.toLowerCase() : "";
      const isTypeNavChar = /^[a-z0-9 ]$/.test(typedChar);
      if (
        menu.multiletterEnabled
        && isTypeNavChar
        && !event.altKey
        && !event.ctrlKey
        && !event.metaKey
        && !event.shiftKey
      ) {
        event.preventDefault();
        menuView.handleTypeNavigation(typedChar);
        return;
      }

      if (!event.ctrlKey && !event.altKey && !event.metaKey) {
        if (event.key === "[") {
          event.preventDefault();
          if (event.shiftKey) {
            onFirstBuffer?.();
          } else {
            onPreviousBuffer?.();
          }
          return;
        }
        if (event.key === "]") {
          event.preventDefault();
          if (event.shiftKey) {
            onLastBuffer?.();
          } else {
            onNextBuffer?.();
          }
          return;
        }
        if (event.key === "," || event.key === "<") {
          event.preventDefault();
          if (event.shiftKey) {
            onOldestMessage?.();
          } else {
            onOlderMessage?.();
          }
          return;
        }
        if (event.key === "." || event.key === ">") {
          event.preventDefault();
          if (event.shiftKey) {
            onNewestMessage?.();
          } else {
            onNewerMessage?.();
          }
          return;
        }
      }
    }

    if (!menuFocused && !typing) {
      return;
    }

    if (event.key === "Escape" || (event.key === "Backspace" && menuFocused && !editing)) {
      if ((event.key === "Escape" || event.key === "Backspace") && menu.menuId === "main_menu") {
        event.preventDefault();
        return;
      }
      event.preventDefault();
      if (
        menu.escapeBehavior === "escape_event"
        || menu.escapeBehavior === "back"
        || menu.escapeBehavior === "select_first_option"
        || menu.escapeBehavior === "select_last_option"
      ) {
        sendEscape();
        return;
      }
      // keybind behavior: send actual key name so server-defined keybinds match.
      const menuIndex = menu.items.length ? menu.selection + 1 : null;
      const currentItem = menu.items[menu.selection] || null;
      sendKeybind({
        key: event.key === "Backspace" ? "backspace" : "escape",
        control: event.ctrlKey,
        alt: event.altKey,
        shift: event.shiftKey,
        menu_id: menu.menuId,
        menu_index: menuIndex,
        menu_item_id: currentItem?.id ?? null,
      });
      return;
    }

    if ((editing || !menuFocused) && event.key !== "Escape") {
      return;
    }

    const key = keyFromEvent(event);
    if (!key) {
      return;
    }

    const menuIndex = menu.items.length ? menu.selection + 1 : null;
    const currentItem = menu.items[menu.selection] || null;

    const isFunctionLike = [
      "escape",
      "space",
      "backspace",
      "enter",
      "up",
      "down",
      "left",
      "right",
      "f1",
      "f2",
      "f3",
      "f4",
      "f5",
      "f6",
      "f7",
      "f8",
      "f9",
      "f10",
    ].includes(key);

    const shouldSend = isFunctionLike || !menu.multiletterEnabled || event.altKey || event.ctrlKey || event.shiftKey;
    if (!shouldSend) {
      return;
    }

    event.preventDefault();
    sendKeybind({
      key,
      control: event.ctrlKey,
      alt: event.altKey,
      shift: event.shiftKey,
      menu_id: menu.menuId,
      menu_index: menuIndex,
      menu_item_id: currentItem?.id ?? null,
    });
  });
}
