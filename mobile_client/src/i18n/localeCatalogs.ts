import catalog_en from "../../locales/en/client.json";
import catalog_es from "../../locales/es/client.json";
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
  "es": {
    name: "Spanish",
    nativeName: "Español",
    contributors: ["UnDuende"],
    official: false,
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
  "es": catalog_es,
  "fa": catalog_fa,
  "vi": catalog_vi,
} as const;

export type MobileLocale = keyof typeof localeCatalogs;
