import catalog_en from "../../locales/en/client.json";
import catalog_fa from "../../locales/fa/client.json";
import catalog_vi from "../../locales/vi/client.json";

export const DEFAULT_LOCALE = "en";

export const LOCALE_METADATA = {
  "en": {
    name: "English",
    nativeName: "English",
    contributors: ["PlayAural core team"],
    official: true,
  },
  "fa": {
    name: "Persian",
    nativeName: "فارسی",
    contributors: ["Hamid Rezaei"],
    official: false,
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
  "fa": catalog_fa,
  "vi": catalog_vi,
} as const;

export type MobileLocale = keyof typeof localeCatalogs;
