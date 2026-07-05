type MenuFocusItem = {
  id?: string;
};

function clampIndex(value: number, length: number): number {
  if (length <= 0) {
    return 0;
  }
  if (!Number.isFinite(value)) {
    return 0;
  }
  return Math.max(0, Math.min(length - 1, value));
}

function stableMenuItemId(item: MenuFocusItem | undefined): string | null {
  return typeof item?.id === "string" && item.id.length > 0 ? item.id : null;
}

function uniqueMenuItemIndexById(items: MenuFocusItem[]): Map<string, number> {
  const counts = new Map<string, number>();
  const indices = new Map<string, number>();
  items.forEach((item, index) => {
    const itemId = stableMenuItemId(item);
    if (!itemId) {
      return;
    }
    counts.set(itemId, (counts.get(itemId) ?? 0) + 1);
    indices.set(itemId, index);
  });
  counts.forEach((count, itemId) => {
    if (count !== 1) {
      indices.delete(itemId);
    }
  });
  return indices;
}

export function resolveMenuFocusIndex(
  previousItems: MenuFocusItem[],
  nextItems: MenuFocusItem[],
  previousIndex: number,
  {
    explicitIndex = null,
    sameMenu,
  }: {
    explicitIndex?: number | null;
    sameMenu: boolean;
  },
): number {
  if (nextItems.length === 0) {
    return 0;
  }
  if (typeof explicitIndex === "number" && Number.isFinite(explicitIndex)) {
    return clampIndex(explicitIndex, nextItems.length);
  }
  if (!sameMenu || previousItems.length === 0) {
    return 0;
  }

  const boundedPreviousIndex = clampIndex(previousIndex, previousItems.length);
  const previousUniqueIndices = uniqueMenuItemIndexById(previousItems);
  const nextUniqueIndices = uniqueMenuItemIndexById(nextItems);

  const previousFocusedId = stableMenuItemId(previousItems[boundedPreviousIndex]);
  if (
    previousFocusedId &&
    previousUniqueIndices.has(previousFocusedId) &&
    nextUniqueIndices.has(previousFocusedId)
  ) {
    return nextUniqueIndices.get(previousFocusedId)!;
  }

  for (let index = boundedPreviousIndex + 1; index < previousItems.length; index += 1) {
    const candidateId = stableMenuItemId(previousItems[index]);
    if (
      candidateId &&
      previousUniqueIndices.has(candidateId) &&
      nextUniqueIndices.has(candidateId)
    ) {
      return nextUniqueIndices.get(candidateId)!;
    }
  }

  for (let index = boundedPreviousIndex - 1; index >= 0; index -= 1) {
    const candidateId = stableMenuItemId(previousItems[index]);
    if (
      candidateId &&
      previousUniqueIndices.has(candidateId) &&
      nextUniqueIndices.has(candidateId)
    ) {
      return nextUniqueIndices.get(candidateId)!;
    }
  }

  return clampIndex(previousIndex, nextItems.length);
}
