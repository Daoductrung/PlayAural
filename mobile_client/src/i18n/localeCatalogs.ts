import catalog_ar from "../../locales/ar/client.json";
import catalog_en from "../../locales/en/client.json";
import catalog_es from "../../locales/es/client.json";
import catalog_fa from "../../locales/fa/client.json";
import catalog_id from "../../locales/id/client.json";
import catalog_pt from "../../locales/pt/client.json";
import catalog_vi from "../../locales/vi/client.json";

export const DEFAULT_LOCALE = "en";

export const LOCALE_METADATA = {
  "ar": {
    name: "Arabic",
    nativeName: "العربية",
    direction: "rtl",
    contributors: ["Lumora Nova team"],
    official: false,
  },
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
    contributors: ["UnDuende", "Tadeu Junior"],
    official: false,
  },
  "fa": {
    name: "Persian",
    nativeName: "فارسی",
    direction: "rtl",
    contributors: ["Hamid Rezaei"],
    official: false,
  },
  "id": {
    name: "Indonesian",
    nativeName: "Bahasa Indonesia",
    direction: "ltr",
    contributors: ["Muhammad", "Komunitas PlayAural Indonesia"],
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
  "ar": catalog_ar,
  "en": catalog_en,
  "es": catalog_es,
  "fa": catalog_fa,
  "id": catalog_id,
  "pt": catalog_pt,
  "vi": catalog_vi,
} as const;

export type MobileLocale = keyof typeof localeCatalogs;
