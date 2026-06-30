import { DEFAULT_LOCALE, LOCALE_METADATA } from "./manifest.js";

export { DEFAULT_LOCALE, LOCALE_METADATA };

export const AVAILABLE_LOCALES = Object.fromEntries(
  Object.entries(LOCALE_METADATA).map(([code, metadata]) => [
    code,
    metadata.nativeName || metadata.name || code,
  ]),
);

export function normalizeLocale(locale) {
  const requested = String(locale || DEFAULT_LOCALE)
    .trim()
    .replaceAll("_", "-")
    .toLowerCase();
  if (Object.prototype.hasOwnProperty.call(LOCALE_METADATA, requested)) {
    return requested;
  }
  const language = requested.split("-")[0];
  return Object.prototype.hasOwnProperty.call(LOCALE_METADATA, language)
    ? language
    : DEFAULT_LOCALE;
}

async function loadCatalog(locale) {
  const normalized = normalizeLocale(locale);
  if (!Object.prototype.hasOwnProperty.call(LOCALE_METADATA, normalized)) {
    throw new Error(`Unsupported locale: ${locale}`);
  }
  const module = await import(`./${normalized}.js`);
  return module.default || {};
}

export async function loadLocaleBundle(locale) {
  const fallback = await loadCatalog(DEFAULT_LOCALE);
  const normalized = normalizeLocale(locale);
  if (normalized === DEFAULT_LOCALE) {
    return {
      locale: DEFAULT_LOCALE,
      messages: fallback,
      fallback,
    };
  }

  try {
    const catalog = await loadCatalog(normalized);
    return {
      locale: normalized,
      messages: { ...fallback, ...catalog },
      fallback,
    };
  } catch {
    return {
      locale: DEFAULT_LOCALE,
      messages: fallback,
      fallback,
    };
  }
}
