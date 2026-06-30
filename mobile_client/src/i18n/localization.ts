import {
  DEFAULT_LOCALE,
  LOCALE_METADATA,
  localeCatalogs,
  type MobileLocale,
} from "./localeCatalogs";

export type { MobileLocale };

type Catalog = Record<string, string>;
const MESSAGE_ALIASES: Record<string, string> = {
  "auth-registration-success": "auth-register-success",
  "error-rate-limit-login": "auth-error-rate-limit",
  "voice-unavailable": "voice-chat-unavailable",
};

function hasOwn<T extends object>(object: T, key: PropertyKey): key is keyof T {
  return Object.prototype.hasOwnProperty.call(object, key);
}

export function resolveMobileLocale(locale: string | undefined): MobileLocale {
  const requested = String(locale || DEFAULT_LOCALE)
    .trim()
    .replaceAll("_", "-")
    .toLowerCase();
  if (hasOwn(localeCatalogs, requested)) {
    return requested;
  }
  const language = requested.split("-")[0];
  if (hasOwn(localeCatalogs, language)) {
    return language;
  }
  return DEFAULT_LOCALE;
}

export class MobileLocalization {
  private locale: MobileLocale = DEFAULT_LOCALE;

  private resolveKey(key: string): string {
    return MESSAGE_ALIASES[key] ?? key;
  }

  resolveLocale(locale: string | undefined): MobileLocale {
    return resolveMobileLocale(locale);
  }

  setLocale(locale: string | undefined): MobileLocale {
    this.locale = this.resolveLocale(locale);
    return this.locale;
  }

  getLocale(): MobileLocale {
    return this.locale;
  }

  getAvailableLocales(): MobileLocale[] {
    return Object.keys(localeCatalogs).sort() as MobileLocale[];
  }

  getLocaleLabel(locale: string | undefined = this.locale): string {
    const resolved = this.resolveLocale(locale);
    const metadata = LOCALE_METADATA[resolved];
    return metadata.nativeName;
  }

  nextLocale(locale: string | undefined = this.locale): MobileLocale {
    const locales = this.getAvailableLocales();
    const current = this.resolveLocale(locale);
    const currentIndex = locales.indexOf(current);
    return locales[(currentIndex + 1) % locales.length] ?? DEFAULT_LOCALE;
  }

  has(key: string): boolean {
    const catalog = localeCatalogs[this.locale] as Catalog;
    const fallback = localeCatalogs[DEFAULT_LOCALE] as Catalog;
    const lookupKey = this.resolveKey(key);
    return hasOwn(catalog, lookupKey) || hasOwn(fallback, lookupKey);
  }

  t(key: string, params: Record<string, string | number> = {}): string {
    const catalog = localeCatalogs[this.locale] as Catalog;
    const fallback = localeCatalogs[DEFAULT_LOCALE] as Catalog;
    const lookupKey = this.resolveKey(key);
    let text = catalog[lookupKey] ?? fallback[lookupKey] ?? key;
    Object.entries(params).forEach(([name, value]) => {
      text = text.replaceAll(`{${name}}`, String(value));
    });
    return text;
  }
}
