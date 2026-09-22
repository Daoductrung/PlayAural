package one.ddt.playaural.spatialaudio

import expo.modules.kotlin.exception.CodedException
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition
import expo.modules.kotlin.records.Field
import expo.modules.kotlin.records.Record

private const val NATIVE_SUCCESS = 0
private const val MAX_SEQUENCE_SEGMENTS = 32
private val SOURCE_ID_PATTERN = Regex("^[A-Za-z0-9_.:-]{1,128}$")

private class SpatialAudioException(message: String) : CodedException(message)

private class SpatialAudioSourceOptions(
  @Field val introPath: String?,
  @Field val loopPath: String,
  @Field val outroPath: String?,
  @Field val playIntro: Boolean,
  @Field val looping: Boolean,
  @Field val streamFromDisk: Boolean,
  @Field val startPaused: Boolean,
  @Field val volume: Double,
  @Field val pitch: Double,
  @Field val x: Double,
  @Field val y: Double,
  @Field val z: Double,
  @Field val spatialBlend: Double,
  @Field val sequencePaths: List<String>?,
  @Field val sequenceNextStartRatios: List<Double>?
) : Record

class PlayAuralSpatialAudioModule : Module() {
  private val lock = Any()
  private val sources = LinkedHashMap<String, Long>()
  private var engineHandle = 0L
  private var engineConfiguration: Triple<Int, Int, Int>? = null

  override fun definition() = ModuleDefinition {
    Name("PlayAuralSpatialAudio")

    AsyncFunction("initialize") {
        hrtfFrameSize: Int,
        parameterSmoothingMilliseconds: Int,
        maxSources: Int ->
      synchronized(lock) {
        initializeEngine(hrtfFrameSize, parameterSmoothingMilliseconds, maxSources)
      }
    }

    AsyncFunction("createSource") { sourceId: String, options: SpatialAudioSourceOptions ->
      synchronized(lock) {
        createSource(sourceId, options)
      }
    }

    Function("setParameters") {
        sourceId: String,
        volume: Double,
        pitch: Double,
        x: Double,
        y: Double,
        z: Double,
        spatialBlend: Double ->
      synchronized(lock) {
        sources[sourceId]?.let { sourceHandle ->
          NativeSpatialAudioBridge.nativeSetParameters(
            sourceHandle,
            volume.toFloat(),
            pitch.toFloat(),
            x.toFloat(),
            y.toFloat(),
            z.toFloat(),
            spatialBlend.toFloat()
          ) == NATIVE_SUCCESS
        } ?: false
      }
    }

    Function("pauseSource") { sourceId: String ->
      synchronized(lock) {
        sources[sourceId]?.let {
          NativeSpatialAudioBridge.nativePauseSource(it) == NATIVE_SUCCESS
        } ?: false
      }
    }

    Function("resumeSource") { sourceId: String ->
      synchronized(lock) {
        sources[sourceId]?.let {
          NativeSpatialAudioBridge.nativeResumeSource(it) == NATIVE_SUCCESS
        } ?: false
      }
    }

    Function("requestOutro") { sourceId: String, finishLoopBoundary: Boolean ->
      synchronized(lock) {
        sources[sourceId]?.let {
          NativeSpatialAudioBridge.nativeRequestOutro(it, finishLoopBoundary) == NATIVE_SUCCESS
        } ?: false
      }
    }

    Function("destroySource") { sourceId: String ->
      synchronized(lock) {
        destroySource(sourceId)
      }
    }

    Function("drainEndedSources") {
      synchronized(lock) {
        val ended = mutableListOf<String>()
        val iterator = sources.iterator()
        while (iterator.hasNext()) {
          val entry = iterator.next()
          if (NativeSpatialAudioBridge.nativeSourceAtEnd(entry.value)) {
            NativeSpatialAudioBridge.nativeDestroySource(entry.value)
            iterator.remove()
            ended.add(entry.key)
          }
        }
        ended
      }
    }

    Function("shutdown") {
      synchronized(lock) {
        shutdown()
      }
    }

    OnDestroy {
      synchronized(lock) {
        shutdown()
      }
    }
  }

  private fun initializeEngine(
    hrtfFrameSize: Int,
    parameterSmoothingMilliseconds: Int,
    maxSources: Int
  ): Map<String, Any> {
    if (hrtfFrameSize <= 0 || parameterSmoothingMilliseconds < 0 || maxSources <= 0) {
      throw SpatialAudioException("Invalid native spatial-audio engine configuration")
    }
    val requested = Triple(hrtfFrameSize, parameterSmoothingMilliseconds, maxSources)
    if (engineHandle != 0L) {
      if (requested != engineConfiguration) {
        throw SpatialAudioException("Native spatial audio is already initialized with different settings")
      }
      return capabilities()
    }
    val result = NativeSpatialAudioBridge.nativeCreateEngine(
      hrtfFrameSize,
      parameterSmoothingMilliseconds,
      maxSources
    )
    if (result.size != 2 || result[0] == 0L || result[1] != NATIVE_SUCCESS.toLong()) {
      throw SpatialAudioException("Native spatial-audio initialization failed (${result.getOrNull(1)})")
    }
    engineHandle = result[0]
    engineConfiguration = requested
    return capabilities()
  }

  private fun capabilities(): Map<String, Any> = mapOf(
    "available" to (engineHandle != 0L),
    "hrtf" to (engineHandle != 0L),
    "sampleRate" to if (engineHandle != 0L) {
      NativeSpatialAudioBridge.nativeEngineSampleRate(engineHandle)
    } else {
      0
    }
  )

  private fun createSource(
    sourceId: String,
    options: SpatialAudioSourceOptions
  ): List<Double> {
    if (engineHandle == 0L) {
      throw SpatialAudioException("Native spatial audio is not initialized")
    }
    val sequencePaths = options.sequencePaths.orEmpty()
    val sequenceNextStartRatios = options.sequenceNextStartRatios.orEmpty()
    val hasStem = options.loopPath.isNotBlank()
    val hasSequence = sequencePaths.isNotEmpty()
    if (
      !SOURCE_ID_PATTERN.matches(sourceId) ||
      hasStem == hasSequence ||
      options.loopPath.contains('\u0000') ||
      options.introPath?.contains('\u0000') == true ||
      options.outroPath?.contains('\u0000') == true ||
      sequencePaths.size > MAX_SEQUENCE_SEGMENTS ||
      sequencePaths.any { it.isBlank() || it.contains('\u0000') } ||
      (hasSequence && sequenceNextStartRatios.size != sequencePaths.size) ||
      sequenceNextStartRatios.any { !it.isFinite() || it < 0.0 || it > 1.0 } ||
      (hasSequence && (
        !options.introPath.isNullOrEmpty() ||
        !options.outroPath.isNullOrEmpty() ||
        options.playIntro ||
        options.looping ||
        options.streamFromDisk
      ))
    ) {
      throw SpatialAudioException("Invalid native spatial-audio source")
    }
    destroySource(sourceId)
    val result = if (hasSequence) {
      NativeSpatialAudioBridge.nativeCreateSequenceSource(
        engineHandle,
        sequencePaths.toTypedArray(),
        sequenceNextStartRatios.map { it.toFloat() }.toFloatArray(),
        options.startPaused,
        options.volume.toFloat(),
        options.pitch.toFloat(),
        options.x.toFloat(),
        options.y.toFloat(),
        options.z.toFloat(),
        options.spatialBlend.toFloat()
      )
    } else {
      NativeSpatialAudioBridge.nativeCreateSource(
        engineHandle,
        options.introPath?.takeIf { it.isNotBlank() },
        options.loopPath,
        options.outroPath?.takeIf { it.isNotBlank() },
        options.playIntro,
        options.looping,
        options.streamFromDisk,
        options.startPaused,
        options.volume.toFloat(),
        options.pitch.toFloat(),
        options.x.toFloat(),
        options.y.toFloat(),
        options.z.toFloat(),
        options.spatialBlend.toFloat()
      )
    }
    if (result.size != 2 || result[0] == 0L || result[1] != NATIVE_SUCCESS.toLong()) {
      throw SpatialAudioException("Native spatial-audio source creation failed (${result.getOrNull(1)})")
    }
    val handle = result[0]
    val durations = if (hasSequence) {
      val sampleRate = NativeSpatialAudioBridge.nativeEngineSampleRate(engineHandle)
      val durationFrames = NativeSpatialAudioBridge.nativeSequenceDurations(handle)
      if (
        sampleRate <= 0 ||
        durationFrames.size != sequencePaths.size ||
        durationFrames.any { it <= 0 }
      ) {
        NativeSpatialAudioBridge.nativeDestroySource(handle)
        throw SpatialAudioException("Native spatial-audio sequence timing is invalid")
      }
      durationFrames.map { frames -> frames.toDouble() * 1000.0 / sampleRate }
    } else {
      emptyList()
    }
    sources[sourceId] = handle
    return durations
  }

  private fun destroySource(sourceId: String) {
    sources.remove(sourceId)?.let { sourceHandle ->
      NativeSpatialAudioBridge.nativeStopSource(sourceHandle)
      NativeSpatialAudioBridge.nativeDestroySource(sourceHandle)
    }
  }

  private fun shutdown() {
    sources.values.forEach { sourceHandle ->
      NativeSpatialAudioBridge.nativeStopSource(sourceHandle)
      NativeSpatialAudioBridge.nativeDestroySource(sourceHandle)
    }
    sources.clear()
    if (engineHandle != 0L) {
      NativeSpatialAudioBridge.nativeDestroyEngine(engineHandle)
      engineHandle = 0L
    }
    engineConfiguration = null
  }
}
