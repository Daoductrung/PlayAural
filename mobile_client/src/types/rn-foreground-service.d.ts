declare module "@supersami/rn-foreground-service" {
  type ForegroundServiceType = "mediaPlayback" | "microphone";

  type ForegroundServiceConfig = {
    ServiceType: ForegroundServiceType;
    icon?: string;
    id: number;
    importance?: "default" | "high" | "low" | "max" | "min" | "none";
    largeIcon?: string;
    message: string;
    setOnlyAlertOnce?: boolean;
    title: string;
    visibility?: "private" | "public" | "secret";
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

  const foregroundService: ForegroundServiceModule;
  export default foregroundService;
}
