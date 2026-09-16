package one.ddt.playaural.spatialaudio

internal object NativeSpatialAudioBridge {
  init {
    System.loadLibrary("playaural_spatial_audio")
  }

  external fun nativeCreateEngine(
    hrtfFrameSize: Int,
    parameterSmoothingMilliseconds: Int,
    maxSources: Int
  ): LongArray
  external fun nativeDestroyEngine(engineHandle: Long)
  external fun nativeEngineSampleRate(engineHandle: Long): Int
  external fun nativeCreateSource(
    engineHandle: Long,
    introPath: String?,
    loopPath: String,
    outroPath: String?,
    playIntro: Boolean,
    looping: Boolean,
    streamFromDisk: Boolean,
    startPaused: Boolean,
    volume: Float,
    pitch: Float,
    x: Float,
    y: Float,
    z: Float,
    spatialBlend: Float
  ): LongArray
  external fun nativeCreateSequenceSource(
    engineHandle: Long,
    sequencePaths: Array<String>,
    startPaused: Boolean,
    volume: Float,
    pitch: Float,
    x: Float,
    y: Float,
    z: Float,
    spatialBlend: Float
  ): LongArray
  external fun nativeSequenceDurations(sourceHandle: Long): LongArray
  external fun nativeDestroySource(sourceHandle: Long)
  external fun nativeSetParameters(
    sourceHandle: Long,
    volume: Float,
    pitch: Float,
    x: Float,
    y: Float,
    z: Float,
    spatialBlend: Float
  ): Int
  external fun nativePauseSource(sourceHandle: Long): Int
  external fun nativeResumeSource(sourceHandle: Long): Int
  external fun nativeRequestOutro(sourceHandle: Long, finishLoopBoundary: Boolean): Int
  external fun nativeStopSource(sourceHandle: Long)
  external fun nativeSourceAtEnd(sourceHandle: Long): Boolean
}
