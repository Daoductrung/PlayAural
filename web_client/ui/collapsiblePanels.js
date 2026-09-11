export function createCollapsiblePanel({ toggleEl, contentEl }) {
  if (!toggleEl || !contentEl) {
    return null;
  }

  let collapsed = toggleEl.getAttribute("aria-expanded") === "false" || contentEl.hidden;

  function render() {
    if (collapsed && contentEl.contains(document.activeElement)) {
      toggleEl.focus({ preventScroll: true });
    }
    toggleEl.setAttribute("aria-expanded", collapsed ? "false" : "true");
    contentEl.hidden = collapsed;
  }

  function setCollapsed(nextCollapsed) {
    collapsed = Boolean(nextCollapsed);
    render();
  }

  toggleEl.addEventListener("click", () => setCollapsed(!collapsed));
  render();

  return {
    isCollapsed: () => collapsed,
    setCollapsed,
  };
}

export function installCollapsiblePanels(root = document) {
  const controllers = new Map();
  for (const panel of root.querySelectorAll("[data-collapsible-panel]")) {
    const controller = createCollapsiblePanel({
      toggleEl: panel.querySelector(".collapsible-panel-toggle"),
      contentEl: panel.querySelector(".collapsible-panel-content"),
    });
    const panelId = panel.dataset.collapsiblePanel?.trim();
    if (controller && panelId) {
      controllers.set(panelId, controller);
    }
  }
  return controllers;
}
