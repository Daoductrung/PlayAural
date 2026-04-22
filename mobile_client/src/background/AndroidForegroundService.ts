import { Platform } from "react-native";

type ForegroundServiceType = "mediaPlayback" | "microphone";

type ForegroundServiceConfig = {
  ServiceType: ForegroundServiceType;
  icon: string;
  id: number;
  importance: "default" | "high" | "low" | "max" | "min" | "none";
  largeIcon: string;
  message: string;
  setOnlyAlertOnce: boolean;
  title: string;
  visibility: "private" | "public" | "secret";
};

type ForegroundServiceModule = {
  is_running: () => boolean;
  register: (options: {
    config?: {
      alert?: boolean;
      onServiceErrorCallBack?: () => void;
    };
  }) => void;
  start: (config: ForegroundServiceConfig) => Promise<void>;
  stop: () => Promise<void>;
  update: (config: ForegroundServiceConfig) => Promise<void>;
};

type SyncOptions = {
  message: string;
  serviceType: ForegroundServiceType;
  title: string;
};

const NOTIFICATION_ID = 44201;

class AndroidForegroundServiceManager {
  private activeSignature = "";
  private initialized = false;
  private module: ForegroundServiceModule | null = null;

  initialize(): void {
    if (this.initialized || Platform.OS !== "android") {
      return;
    }
    this.initialized = true;
    try {
      const requiredModule =
        require("@supersami/rn-foreground-service") as { default?: ForegroundServiceModule };
      this.module = requiredModule.default ?? null;
      this.module?.register({
        config: {
          alert: false,
        },
      });
    } catch (error) {
      this.module = null;
      console.warn("PlayAural: foreground service bootstrap failed.", error);
    }
  }

  async sync(options: SyncOptions): Promise<void> {
    if (Platform.OS !== "android") {
      return;
    }
    this.initialize();
    if (!this.module) {
      return;
    }

    const config: ForegroundServiceConfig = {
      ServiceType: options.serviceType,
      icon: "ic_launcher",
      id: NOTIFICATION_ID,
      importance: "low",
      largeIcon: "ic_launcher",
      message: options.message,
      setOnlyAlertOnce: true,
      title: options.title,
      visibility: "public",
    };
    const signature = JSON.stringify(config);
    if (signature === this.activeSignature && this.module.is_running()) {
      return;
    }

    try {
      if (this.module.is_running()) {
        await this.module.update(config);
      } else {
        await this.module.start(config);
      }
      this.activeSignature = signature;
    } catch (error) {
      console.warn("PlayAural: foreground service sync failed.", error);
    }
  }

  async stop(): Promise<void> {
    this.initialize();
    if (!this.module) {
      return;
    }
    this.activeSignature = "";
    if (!this.module.is_running()) {
      return;
    }
    try {
      await this.module.stop();
    } catch (error) {
      console.warn("PlayAural: foreground service stop failed.", error);
    }
  }
}

export const androidForegroundService = new AndroidForegroundServiceManager();

export function initializeAndroidForegroundService(): void {
  androidForegroundService.initialize();
}
