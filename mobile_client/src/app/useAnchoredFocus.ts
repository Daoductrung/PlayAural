import { useCallback, useState, type SetStateAction } from "react";
import { resolveMenuFocusIndex } from "./menuFocus";

// Reconcile before rendering or speaking a changed list, so a newly inserted
// message cannot briefly replace the user's focused message at the old index.
export function useAnchoredFocus<T extends { id: string }>(items: T[]) {
  const [selection, setSelection] = useState({ items, index: 0 });
  const index = selection.items === items ? selection.index
    : resolveMenuFocusIndex(selection.items, items, selection.index, { sameMenu: true });
  if (selection.items !== items) setSelection({ items, index });
  const setIndex = useCallback((update: SetStateAction<number>) => {
    setSelection((previous) => {
      const current = previous.items === items ? previous.index
        : resolveMenuFocusIndex(previous.items, items, previous.index, { sameMenu: true });
      const next = typeof update === "function" ? update(current) : update;
      const bounded = Math.max(0, Math.min(Math.max(0, items.length - 1), next));
      return previous.items === items && previous.index === bounded ? previous : { items, index: bounded };
    });
  }, [items]);
  return [index, setIndex] as const;
}
