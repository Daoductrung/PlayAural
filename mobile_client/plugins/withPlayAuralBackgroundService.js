const fs = require("fs");
const path = require("path");

const {
  withAppBuildGradle,
  withAndroidManifest,
  withDangerousMod,
  withMainActivity,
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

function getGestureConfigurationModuleSource(packageName) {
  return `package ${packageName}

import android.util.TypedValue
import android.view.ViewConfiguration

import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule

class GestureConfigurationModule(
  private val reactContext: ReactApplicationContext,
) : ReactContextBaseJavaModule(reactContext) {
  companion object {
    private const val PATH_SAMPLE_DISTANCE_MM = 2.5f
    private const val SWIPE_CONFIRMATION_DISTANCE_MM = 10f
  }

  override fun getName(): String = "PlayAuralGestureConfiguration"

  override fun getConstants(): Map<String, Any> {
    val displayMetrics = reactContext.resources.displayMetrics
    val density = displayMetrics.density.coerceAtLeast(1f)
    val viewConfiguration = ViewConfiguration.get(reactContext)
    val sampleDistanceDp = TypedValue.applyDimension(
      TypedValue.COMPLEX_UNIT_MM,
      PATH_SAMPLE_DISTANCE_MM,
      displayMetrics,
    ) / density
    val swipeConfirmationDistanceDp = TypedValue.applyDimension(
      TypedValue.COMPLEX_UNIT_MM,
      SWIPE_CONFIRMATION_DISTANCE_MM,
      displayMetrics,
    ) / density

    return mapOf(
      "doubleTapSlopDp" to viewConfiguration.scaledDoubleTapSlop / density,
      "longPressTimeoutMs" to ViewConfiguration.getLongPressTimeout(),
      "multiTapTimeoutMs" to ViewConfiguration.getDoubleTapTimeout(),
      "pathSampleDistanceDp" to sampleDistanceDp,
      "singleFingerSwipeConfirmDistanceDp" to swipeConfirmationDistanceDp,
      "touchSlopDp" to viewConfiguration.scaledTouchSlop / density,
    )
  }
}
`;
}

function getGestureInputModuleSource(packageName) {
  return `package ${packageName}

import android.view.MotionEvent

import com.facebook.react.bridge.Arguments
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.WritableArray
import com.facebook.react.bridge.WritableMap

class GestureInputModule(
  private val reactContext: ReactApplicationContext,
) : ReactContextBaseJavaModule(reactContext) {
  companion object {
    private const val EVENT_NAME = "PlayAuralGestureFrames"

    @Volatile
    private var activeModule: GestureInputModule? = null

    fun dispatchTouchEvent(event: MotionEvent) {
      activeModule?.handleTouchEvent(event)
    }
  }

  private var forwardingMultiTouch = false
  private var pendingDownFrame: WritableMap? = null
  private val displayDensity = reactContext.resources.displayMetrics.density.coerceAtLeast(1f)

  override fun getName(): String = "PlayAuralGestureInput"

  override fun getConstants(): Map<String, Any> = mapOf(
    "available" to true,
    "eventName" to EVENT_NAME,
  )

  override fun initialize() {
    super.initialize()
    activeModule = this
  }

  override fun invalidate() {
    if (activeModule === this) {
      activeModule = null
    }
    resetGesture()
    super.invalidate()
  }

  private fun handleTouchEvent(event: MotionEvent) {
    when (event.actionMasked) {
      MotionEvent.ACTION_DOWN -> {
        resetGesture()
        pendingDownFrame = createTransitionFrame(
          event,
          phase = "start",
          startsGesture = true,
        )
      }
      MotionEvent.ACTION_POINTER_DOWN -> {
        val frame = createTransitionFrame(
          event,
          phase = "start",
          startsGesture = false,
        )
        if (!forwardingMultiTouch && event.pointerCount >= 2) {
          forwardingMultiTouch = true
          val frames = mutableListOf<WritableMap>()
          pendingDownFrame?.let(frames::add)
          frames.add(frame)
          pendingDownFrame = null
          emitFrames(frames)
        } else if (forwardingMultiTouch) {
          emitFrames(listOf(frame))
        }
      }
      MotionEvent.ACTION_MOVE -> {
        if (forwardingMultiTouch) {
          emitFrames(createMoveFrames(event))
        }
      }
      MotionEvent.ACTION_POINTER_UP -> {
        if (forwardingMultiTouch) {
          emitFrames(
            listOf(
              createTransitionFrame(
                event,
                phase = "end",
                startsGesture = false,
              ),
            ),
          )
        }
      }
      MotionEvent.ACTION_UP -> {
        if (forwardingMultiTouch) {
          emitFrames(
            listOf(
              createTransitionFrame(
                event,
                phase = "end",
                startsGesture = false,
              ),
            ),
          )
        }
        resetGesture()
      }
      MotionEvent.ACTION_CANCEL -> {
        if (forwardingMultiTouch) {
          emitFrames(
            listOf(
              createTransitionFrame(
                event,
                phase = "cancel",
                startsGesture = false,
              ),
            ),
          )
        }
        resetGesture()
      }
    }
  }

  private fun createMoveFrames(event: MotionEvent): List<WritableMap> {
    val frames = mutableListOf<WritableMap>()
    for (historyIndex in 0 until event.historySize) {
      frames.add(createMoveFrame(event, historyIndex))
    }
    frames.add(createMoveFrame(event, historyIndex = null))
    return frames
  }

  private fun createMoveFrame(event: MotionEvent, historyIndex: Int?): WritableMap {
    val touches = createTouchArray(
      event,
      excludedPointerIndex = null,
      historyIndex = historyIndex,
    )
    return createFrame(
      activeTouchCount = event.pointerCount,
      changedTouches = Arguments.createArray(),
      phase = "move",
      startsGesture = false,
      timestamp = if (historyIndex == null) {
        event.eventTime
      } else {
        event.getHistoricalEventTime(historyIndex)
      },
      touches = touches,
    )
  }

  private fun createTransitionFrame(
    event: MotionEvent,
    phase: String,
    startsGesture: Boolean,
  ): WritableMap {
    val endedPointerIndex = when (event.actionMasked) {
      MotionEvent.ACTION_POINTER_UP,
      MotionEvent.ACTION_UP -> event.actionIndex
      else -> null
    }
    val activeTouchCount = when (event.actionMasked) {
      MotionEvent.ACTION_POINTER_UP -> event.pointerCount - 1
      MotionEvent.ACTION_UP,
      MotionEvent.ACTION_CANCEL -> 0
      else -> event.pointerCount
    }
    val changedTouches = when (event.actionMasked) {
      MotionEvent.ACTION_CANCEL -> createTouchArray(
        event,
        excludedPointerIndex = null,
        historyIndex = null,
      )
      else -> Arguments.createArray().apply {
        pushMap(createTouch(event, event.actionIndex, historyIndex = null))
      }
    }
    return createFrame(
      activeTouchCount = activeTouchCount,
      changedTouches = changedTouches,
      phase = phase,
      startsGesture = startsGesture,
      timestamp = event.eventTime,
      touches = if (event.actionMasked == MotionEvent.ACTION_CANCEL) {
        Arguments.createArray()
      } else {
        createTouchArray(
          event,
          excludedPointerIndex = endedPointerIndex,
          historyIndex = null,
        )
      },
    )
  }

  private fun createFrame(
    activeTouchCount: Int,
    changedTouches: WritableArray,
    phase: String,
    startsGesture: Boolean,
    timestamp: Long,
    touches: WritableArray,
  ): WritableMap = Arguments.createMap().apply {
    putInt("activeTouchCount", activeTouchCount)
    putArray("changedTouches", changedTouches)
    putString("phase", phase)
    putBoolean("startsGesture", startsGesture)
    putDouble("timestamp", timestamp.toDouble())
    putArray("touches", touches)
  }

  private fun createTouchArray(
    event: MotionEvent,
    excludedPointerIndex: Int?,
    historyIndex: Int?,
  ): WritableArray = Arguments.createArray().apply {
    for (pointerIndex in 0 until event.pointerCount) {
      if (pointerIndex != excludedPointerIndex) {
        pushMap(createTouch(event, pointerIndex, historyIndex))
      }
    }
  }

  private fun createTouch(
    event: MotionEvent,
    pointerIndex: Int,
    historyIndex: Int?,
  ): WritableMap {
    val x = if (historyIndex == null) {
      event.getX(pointerIndex)
    } else {
      event.getHistoricalX(pointerIndex, historyIndex)
    }
    val y = if (historyIndex == null) {
      event.getY(pointerIndex)
    } else {
      event.getHistoricalY(pointerIndex, historyIndex)
    }
    return Arguments.createMap().apply {
      putInt("identifier", event.getPointerId(pointerIndex))
      putDouble("pageX", (x / displayDensity).toDouble())
      putDouble("pageY", (y / displayDensity).toDouble())
    }
  }

  private fun emitFrames(frames: List<WritableMap>) {
    if (
      frames.isEmpty() ||
      !reactContext.hasActiveReactInstance()
    ) {
      return
    }
    val frameArray = Arguments.createArray()
    frames.forEach(frameArray::pushMap)
    val payload = Arguments.createMap().apply {
      putArray("frames", frameArray)
    }
    reactContext.emitDeviceEvent(EVENT_NAME, payload)
  }

  private fun resetGesture() {
    forwardingMultiTouch = false
    pendingDownFrame = null
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
    listOf(
      BatteryOptimizationModule(reactContext),
      GestureConfigurationModule(reactContext),
      GestureInputModule(reactContext),
    )

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

function withPlayAuralMainActivity(config) {
  return withMainActivity(config, (nextConfig) => {
    if (nextConfig.modResults.language !== "kt") {
      throw new Error(
        "PlayAural gesture input requires the generated Android MainActivity to use Kotlin.",
      );
    }
    let contents = nextConfig.modResults.contents;
    if (!contents.includes("import android.view.MotionEvent")) {
      contents = contents.replace(
        /^(package\s+[^\r\n]+\r?\n)/,
        `$1\nimport android.view.MotionEvent\n`,
      );
    }
    if (!contents.includes("GestureInputModule.dispatchTouchEvent(event)")) {
      const activityDeclaration = /class MainActivity\s*:\s*ReactActivity\(\)\s*\{/;
      if (!activityDeclaration.test(contents)) {
        throw new Error(
          "Unable to install PlayAural's raw Android gesture observer. "
            + "Review the generated MainActivity structure.",
        );
      }
      contents = contents.replace(
        activityDeclaration,
        (match) => `${match}\n  override fun dispatchTouchEvent(event: MotionEvent): Boolean {\n    GestureInputModule.dispatchTouchEvent(event)\n    return super.dispatchTouchEvent(event)\n  }\n`,
      );
    }
    nextConfig.modResults.contents = contents;
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
        path.join(targetDir, "GestureConfigurationModule.kt"),
        getGestureConfigurationModuleSource(packageName),
      );
      fs.writeFileSync(
        path.join(targetDir, "GestureInputModule.kt"),
        getGestureInputModuleSource(packageName),
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
  nextConfig = withPlayAuralMainActivity(nextConfig);
  nextConfig = withPlayAuralNativeFiles(nextConfig);
  nextConfig = withPlayAuralDebugApplicationId(nextConfig);
  return nextConfig;
};
