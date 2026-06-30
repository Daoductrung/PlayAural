import catalog_en from "../../locales/en/client.json";
import catalog_vi from "../../locales/vi/client.json";

export const DEFAULT_LOCALE = "en";

export const LOCALE_METADATA = {
  "en": {
    name: "English",
    nativeName: "English",
    contributors: ["PlayAural core team"],
    official: true,
  },
  "vi": {
    name: "Vietnamese",
    nativeName: "Tiếng Việt",
    contributors: ["Trung", "PlayAural core team"],
    official: true,
  },
} as const;

export const localeCatalogs = {
  "en": catalog_en,
  "vi": catalog_vi,
} as const;

export type MobileLocale = keyof typeof localeCatalogs;
