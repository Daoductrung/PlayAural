const fs = require("fs");
const path = require("path");

const {
  withAppBuildGradle,
  withAndroidManifest,
  withDangerousMod,
  withMainApplication,
} = require("@expo/config-plugins");

const NATIVE_PACKAGE_NAME = "PlayAuralNativePackage";

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

function getAndroidPackageName(config) {
  return config.android?.package || "one.ddt.playaural.mobile";
}

function getBatteryOptimizationModuleSource(packageName) {
  return `package ${packageName}

import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.PowerManager
import android.provider.Settings

import com.facebook.react.bridge.Promise
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod

class BatteryOptimizationModule(
  private val reactContext: ReactApplicationContext,
) : ReactContextBaseJavaModule(reactContext) {
  private var wakeLock: PowerManager.WakeLock? = null

  override fun getName(): String = "PlayAuralBatteryOptimization"

  @ReactMethod
  fun isIgnoringBatteryOptimizations(promise: Promise) {
    if (Build.VERSION.SDK_INT < Build.VERSION_CODES.M) {
      promise.resolve(true)
      return
    }

    val powerManager = reactContext.getSystemService(Context.POWER_SERVICE) as? PowerManager
    promise.resolve(powerManager?.isIgnoringBatteryOptimizations(reactContext.packageName) == true)
  }

  @ReactMethod
  fun requestIgnoreBatteryOptimizations(promise: Promise) {
    if (Build.VERSION.SDK_INT < Build.VERSION_CODES.M) {
      promise.resolve(false)
      return
    }

    val powerManager = reactContext.getSystemService(Context.POWER_SERVICE) as? PowerManager
    if (powerManager?.isIgnoringBatteryOptimizations(reactContext.packageName) == true) {
      promise.resolve(false)
      return
    }

    val intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS).apply {
      data = Uri.parse("package:\${reactContext.packageName}")
    }
    val activity = reactApplicationContext.currentActivity
    if (activity == null) {
      intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    }

    try {
      (activity ?: reactContext).startActivity(intent)
      promise.resolve(true)
    } catch (error: ActivityNotFoundException) {
      promise.resolve(false)
    } catch (error: SecurityException) {
      promise.resolve(false)
    }
  }

  @ReactMethod
  fun setPartialWakeLockEnabled(enabled: Boolean, promise: Promise) {
    try {
      if (enabled) {
        acquireWakeLock()
      } else {
        releaseWakeLock()
      }
      promise.resolve(true)
    } catch (error: SecurityException) {
      promise.resolve(false)
    }
  }

  override fun invalidate() {
    releaseWakeLock()
    super.invalidate()
  }

  private fun acquireWakeLock() {
    val existing = wakeLock
    if (existing?.isHeld == true) {
      return
    }

    val powerManager = reactContext.getSystemService(Context.POWER_SERVICE) as? PowerManager
      ?: return
    wakeLock = powerManager.newWakeLock(
      PowerManager.PARTIAL_WAKE_LOCK,
      "\${reactContext.packageName}:PlayAuralBackground",
    ).apply {
      setReferenceCounted(false)
      acquire()
    }
  }

  private fun releaseWakeLock() {
    val existing = wakeLock
    wakeLock = null
    if (existing?.isHeld == true) {
      existing.release()
    }
  }
}
`;
}

function getNativePackageSource(packageName) {
  return `package ${packageName}

import com.facebook.react.ReactPackage
import com.facebook.react.bridge.NativeModule
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.uimanager.ViewManager

class PlayAuralNativePackage : ReactPackage {
  override fun createNativeModules(reactContext: ReactApplicationContext): List<NativeModule> =
    listOf(BatteryOptimizationModule(reactContext))

  override fun createViewManagers(
    reactContext: ReactApplicationContext,
  ): List<ViewManager<*, *>> = emptyList()
}
`;
}

function withPlayAuralManifest(config) {
  return withAndroidManifest(config, (nextConfig) => {
    const manifest = nextConfig.modResults.manifest;
    const application = manifest.application?.[0];
    if (!application) {
      return nextConfig;
    }

    [
      "android.permission.FOREGROUND_SERVICE",
      "android.permission.FOREGROUND_SERVICE_DATA_SYNC",
      "android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK",
      "android.permission.FOREGROUND_SERVICE_MICROPHONE",
      "android.permission.POST_NOTIFICATIONS",
      "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS",
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
      "Keeps PlayAural gameplay, voice chat, and audio active when needed.",
    );
    ensureService(application, "com.supersami.foregroundservice.ForegroundService", {
      "android:exported": "false",
      "android:foregroundServiceType": "dataSync|mediaPlayback|microphone",
      "android:stopWithTask": "false",
    });
    ensureService(application, "com.supersami.foregroundservice.ForegroundServiceTask", {
      "android:exported": "false",
      "android:stopWithTask": "false",
    });

    return nextConfig;
  });
}

function withPlayAuralMainApplication(config) {
  return withMainApplication(config, (nextConfig) => {
    const contents = nextConfig.modResults.contents;
    if (contents.includes(`add(${NATIVE_PACKAGE_NAME}())`)) {
      return nextConfig;
    }

    nextConfig.modResults.contents = contents.replace(
      /PackageList\(this\)\.packages\.apply\s*\{/,
      (match) => `${match}\n          add(${NATIVE_PACKAGE_NAME}())`,
    );
    return nextConfig;
  });
}

function withPlayAuralNativeFiles(config) {
  return withDangerousMod(config, [
    "android",
    (nextConfig) => {
      const packageName = getAndroidPackageName(nextConfig);
      const packagePath = packageName.split(".").join(path.sep);
      const targetDir = path.join(
        nextConfig.modRequest.platformProjectRoot,
        "app",
        "src",
        "main",
        "java",
        packagePath,
      );
      fs.mkdirSync(targetDir, { recursive: true });
      fs.writeFileSync(
        path.join(targetDir, "BatteryOptimizationModule.kt"),
        getBatteryOptimizationModuleSource(packageName),
      );
      fs.writeFileSync(
        path.join(targetDir, "PlayAuralNativePackage.kt"),
        getNativePackageSource(packageName),
      );
      return nextConfig;
    },
  ]);
}

function withPlayAuralDebugApplicationId(config) {
  return withAppBuildGradle(config, (nextConfig) => {
    const suffixLine = 'applicationIdSuffix ".debug"';
    if (nextConfig.modResults.contents.includes(suffixLine)) {
      return nextConfig;
    }
    const debugBlock = /(buildTypes\s*\{\s*debug\s*\{)/;
    if (!debugBlock.test(nextConfig.modResults.contents)) {
      throw new Error(
        "Unable to isolate the PlayAural Android debug application ID. "
          + "Review the generated app/build.gradle structure.",
      );
    }
    nextConfig.modResults.contents = nextConfig.modResults.contents.replace(
      debugBlock,
      `$1\n            ${suffixLine}`,
    );
    return nextConfig;
  });
}

module.exports = function withPlayAuralBackgroundService(config) {
  let nextConfig = withPlayAuralManifest(config);
  nextConfig = withPlayAuralMainApplication(nextConfig);
  nextConfig = withPlayAuralNativeFiles(nextConfig);
  nextConfig = withPlayAuralDebugApplicationId(nextConfig);
  return nextConfig;
};
