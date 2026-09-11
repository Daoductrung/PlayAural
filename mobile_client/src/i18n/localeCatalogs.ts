import catalog_en from "../../locales/en/client.json";
import catalog_es from "../../locales/es/client.json";
import catalog_fa from "../../locales/fa/client.json";
import catalog_pt from "../../locales/pt/client.json";
import catalog_vi from "../../locales/vi/client.json";

export const DEFAULT_LOCALE = "en";

export const LOCALE_METADATA = {
  "en": {
    name: "English",
    nativeName: "English",
    direction: "ltr",
    contributors: ["PlayAural core team"],
    official: true,
  },
  "es": {
    name: "Spanish",
    nativeName: "Español",
    direction: "ltr",
    contributors: ["UnDuende"],
    official: false,
  },
  "fa": {
    name: "Persian",
    nativeName: "فارسی",
    direction: "rtl",
    contributors: ["Hamid Rezaei"],
    official: false,
  },
  "pt": {
    name: "Portuguese (Brazil)",
    nativeName: "Português (Brasil)",
    direction: "ltr",
    contributors: ["Tadeu Junior"],
    official: false,
  },
  "vi": {
    name: "Vietnamese",
    nativeName: "Tiếng Việt",
    direction: "ltr",
    contributors: ["Trung", "PlayAural core team"],
    official: true,
  },
} as const;

export const localeCatalogs = {
  "en": catalog_en,
  "es": catalog_es,
  "fa": catalog_fa,
  "pt": catalog_pt,
  "vi": catalog_vi,
} as const;

export type MobileLocale = keyof typeof localeCatalogs;
