// Fit small boards to their viewport without shrinking controls below their
// accessible size. Larger boards retain that size and scroll on either axis.
export function gridCellSizeForViewport(
  columns: number, rows: number, width: number, height: number, gap: number, minimum: number,
): number {
  const fittedWidth = (width - gap * Math.max(0, columns - 1)) / Math.max(1, columns);
  const fittedHeight = (height - gap * Math.max(0, rows - 1)) / Math.max(1, rows);
  return Math.max(minimum, Math.min(fittedWidth, fittedHeight));
}
