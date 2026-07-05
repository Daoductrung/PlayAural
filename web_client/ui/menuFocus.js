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
