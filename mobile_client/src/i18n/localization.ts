import en from "../../locales/en/client.json";
import vi from "../../locales/vi/client.json";

const catalogs = {
  en,
  vi,
};

export type MobileLocale = keyof typeof catalogs;

export class MobileLocalization {
  private locale: MobileLocale = "en";

  setLocale(locale: string | undefined): void {
    if (locale === "vi") {
      this.locale = "vi";
      return;
    }
    this.locale = "en";
  }

  getLocale(): MobileLocale {
    return this.locale;
  }

  has(key: string): boolean {
    const catalog = catalogs[this.locale] as Record<string, string>;
    return Object.prototype.hasOwnProperty.call(catalog, key) || Object.prototype.hasOwnProperty.call(catalogs.en, key);
  }

  t(key: string, params: Record<string, string | number> = {}): string {
    const catalog = catalogs[this.locale] as Record<string, string>;
    let text = catalog[key] ?? catalogs.en[key as keyof typeof en] ?? key;
    Object.entries(params).forEach(([name, value]) => {
      text = text.replaceAll(`{${name}}`, String(value));
    });
    return text;
  }
}
