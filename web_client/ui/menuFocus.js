const MAX_MENU_FOCUS_CONTEXTS = 8;
const MAX_MENU_FOCUS_CONTEXT_ID_LENGTH = 128;

function validFocusContextId(contextId) {
  return typeof contextId === "string"
    && contextId.length > 0
    && contextId.length <= MAX_MENU_FOCUS_CONTEXT_ID_LENGTH
    && contextId.trim() === contextId;
}

export class MenuFocusContextStore {
  constructor(capacity = MAX_MENU_FOCUS_CONTEXTS) {
    if (!Number.isInteger(capacity) || capacity <= 0) {
      throw new TypeError("Menu focus context capacity must be a positive integer");
    }
    this.capacity = capacity;
    this.contexts = new Map();
  }

  capture(contextId, context) {
    if (!validFocusContextId(contextId)) {
      return;
    }
    this.contexts.delete(contextId);
    this.contexts.set(contextId, context);
    while (this.contexts.size > this.capacity) {
      this.contexts.delete(this.contexts.keys().next().value);
    }
  }

  consume(contextId) {
    if (!validFocusContextId(contextId)) {
      return null;
    }
    const context = this.contexts.get(contextId) || null;
    this.contexts.delete(contextId);
    return context;
  }

  clear() {
    this.contexts.clear();
  }

  get size() {
    return this.contexts.size;
  }
}

function clampIndex(value, length) {
  if (length <= 0) {
    return 0;
  }
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return 0;
  }
  return Math.max(0, Math.min(length - 1, number));
}

export function stableMenuItemId(item) {
  return typeof item?.id === "string" && item.id.length > 0 ? item.id : null;
}

function uniqueMenuItemIndexById(items) {
  const counts = new Map();
  const indices = new Map();
  items.forEach((item, index) => {
    const itemId = stableMenuItemId(item);
    if (!itemId) {
      return;
    }
    counts.set(itemId, (counts.get(itemId) || 0) + 1);
    indices.set(itemId, index);
  });
  counts.forEach((count, itemId) => {
    if (count !== 1) {
      indices.delete(itemId);
    }
  });
  return indices;
}

export function resolveMenuFocusIndex(previousItems, nextItems, previousIndex, {
  sameMenu,
  explicitIndex = null,
} = {}) {
  if (!nextItems.length) {
    return 0;
  }
  if (explicitIndex !== null && explicitIndex !== undefined) {
    return clampIndex(explicitIndex, nextItems.length);
  }
  if (!sameMenu || !previousItems.length) {
    return 0;
  }

  const boundedPreviousIndex = clampIndex(previousIndex, previousItems.length);
  const previousUniqueIndices = uniqueMenuItemIndexById(previousItems);
  const nextUniqueIndices = uniqueMenuItemIndexById(nextItems);

  const previousFocusedId = stableMenuItemId(previousItems[boundedPreviousIndex]);
  if (previousUniqueIndices.has(previousFocusedId) && nextUniqueIndices.has(previousFocusedId)) {
    return nextUniqueIndices.get(previousFocusedId);
  }

  for (let index = boundedPreviousIndex + 1; index < previousItems.length; index += 1) {
    const candidateId = stableMenuItemId(previousItems[index]);
    if (previousUniqueIndices.has(candidateId) && nextUniqueIndices.has(candidateId)) {
      return nextUniqueIndices.get(candidateId);
    }
  }

  for (let index = boundedPreviousIndex - 1; index >= 0; index -= 1) {
    const candidateId = stableMenuItemId(previousItems[index]);
    if (previousUniqueIndices.has(candidateId) && nextUniqueIndices.has(candidateId)) {
      return nextUniqueIndices.get(candidateId);
    }
  }

  return clampIndex(previousIndex, nextItems.length);
}
