const { withAndroidManifest } = require("@expo/config-plugins");

function ensureUsesPermission(manifest, permissionName) {
  const permissions = manifest["uses-permission"] ?? [];
  const exists = permissions.some((entry) => entry?.$?.["android:name"] === permissionName);
  if (!exists) {
    permissions.push({
      $: {
        "android:name": permissionName,
      },
    });
  }
  manifest["uses-permission"] = permissions;
}

function ensureMetadata(application, name, value) {
  const metadata = application["meta-data"] ?? [];
  const existing = metadata.find((entry) => entry?.$?.["android:name"] === name);
  if (existing) {
    existing.$["android:value"] = value;
    return;
  }
  metadata.push({
    $: {
      "android:name": name,
      "android:value": value,
    },
  });
  application["meta-data"] = metadata;
}

function ensureService(application, name, extraAttributes = {}) {
  const services = application.service ?? [];
  const existing = services.find((entry) => entry?.$?.["android:name"] === name);
  if (existing) {
    existing.$ = {
      ...existing.$,
      ...extraAttributes,
    };
  } else {
    services.push({
      $: {
        "android:name": name,
        ...extraAttributes,
      },
    });
  }
  application.service = services;
}

module.exports = function withPlayAuralBackgroundService(config) {
  return withAndroidManifest(config, (nextConfig) => {
    const manifest = nextConfig.modResults.manifest;
    const application = manifest.application?.[0];
    if (!application) {
      return nextConfig;
    }

    [
      "android.permission.FOREGROUND_SERVICE",
      "android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK",
      "android.permission.FOREGROUND_SERVICE_MICROPHONE",
      "android.permission.POST_NOTIFICATIONS",
      "android.permission.WAKE_LOCK",
    ].forEach((permissionName) => {
      ensureUsesPermission(manifest, permissionName);
    });

    ensureMetadata(
      application,
      "com.supersami.foregroundservice.notification_channel_name",
      "PlayAural background activity",
    );
    ensureMetadata(
      application,
      "com.supersami.foregroundservice.notification_channel_description",
      "Keeps PlayAural voice chat and audio active when needed.",
    );
    ensureService(application, "com.supersami.foregroundservice.ForegroundService", {
      "android:exported": "false",
      "android:foregroundServiceType": "mediaPlayback|microphone",
      "android:stopWithTask": "false",
    });
    ensureService(application, "com.supersami.foregroundservice.ForegroundServiceTask", {
      "android:exported": "false",
      "android:stopWithTask": "false",
    });

    return nextConfig;
  });
};
