import ExpoModulesCore
import Foundation

private let nativeSuccess: Int32 = 0
private let maxSequenceSegments = 32
private let sourceIDPattern = try! NSRegularExpression(
  pattern: "^[A-Za-z0-9_.:-]{1,128}$"
)

private final class SpatialAudioException: GenericException<String> {
  override var reason: String {
    param
  }
}

private struct SpatialAudioSourceOptions: Record {
  @Field var introPath: String?
  @Field var loopPath: String = ""
  @Field var outroPath: String?
  @Field var playIntro: Bool = false
  @Field var looping: Bool = false
  @Field var streamFromDisk: Bool = false
  @Field var startPaused: Bool = false
  @Field var volume: Double = 1
  @Field var pitch: Double = 1
  @Field var x: Double = 0
  @Field var y: Double = 0
  @Field var z: Double = 0
  @Field var spatialBlend: Double = 1
  @Field var sequencePaths: [String] = []
  @Field var sequenceNextStartRatios: [Double] = []
}

public final class PlayAuralSpatialAudioModule: Module {
  private let lock = NSLock()
  private var engineHandle: UInt = 0
  private var engineConfiguration: [Int]?
  private var sources: [String: UInt] = [:]

  public func definition() -> ModuleDefinition {
    Name("PlayAuralSpatialAudio")

    AsyncFunction("initialize") {
        (hrtfFrameSize: Int, parameterSmoothingMilliseconds: Int, maxSources: Int) in
      try self.withLock {
        try self.initializeEngine(
          hrtfFrameSize: hrtfFrameSize,
          parameterSmoothingMilliseconds: parameterSmoothingMilliseconds,
          maxSources: maxSources
        )
      }
    }

    AsyncFunction("createSource") {
        (sourceID: String, options: SpatialAudioSourceOptions) in
      try self.withLock {
        try self.createSource(sourceID: sourceID, options: options)
      }
    }

    Function("setParameters") {
        (
          sourceID: String,
          volume: Double,
          pitch: Double,
          x: Double,
          y: Double,
          z: Double,
          spatialBlend: Double
        ) -> Bool in
      self.withLock {
        guard let source = self.sources[sourceID] else { return false }
        return PASetSpatialAudioSourceParameters(
          source,
          Float(volume),
          Float(pitch),
          Float(x),
          Float(y),
          Float(z),
          Float(spatialBlend)
        ) == nativeSuccess
      }
    }

    Function("pauseSource") { (sourceID: String) -> Bool in
      self.withLock {
        self.sources[sourceID].map { PAPauseSpatialAudioSource($0) == nativeSuccess } ?? false
      }
    }

    Function("resumeSource") { (sourceID: String) -> Bool in
      self.withLock {
        self.sources[sourceID].map { PAResumeSpatialAudioSource($0) == nativeSuccess } ?? false
      }
    }

    Function("requestOutro") { (sourceID: String, finishLoopBoundary: Bool) -> Bool in
      self.withLock {
        self.sources[sourceID].map {
          PARequestSpatialAudioSourceOutro($0, finishLoopBoundary) == nativeSuccess
        } ?? false
      }
    }

    Function("destroySource") { (sourceID: String) in
      self.withLock { self.destroySource(sourceID) }
    }

    Function("drainEndedSources") { () -> [String] in
      self.withLock {
        let ended = self.sources.compactMap { key, source in
          PASpatialAudioSourceAtEnd(source) ? key : nil
        }
        ended.forEach { self.destroySource($0) }
        return ended
      }
    }

    Function("shutdown") {
      self.withLock { self.shutdown() }
    }

    OnDestroy {
      self.withLock { self.shutdown() }
    }
  }

  private func withLock<T>(_ operation: () throws -> T) rethrows -> T {
    lock.lock()
    defer { lock.unlock() }
    return try operation()
  }

  private func initializeEngine(
    hrtfFrameSize: Int,
    parameterSmoothingMilliseconds: Int,
    maxSources: Int
  ) throws -> [String: Any] {
    guard
      let nativeHrtfFrameSize = Int32(exactly: hrtfFrameSize),
      let nativeParameterSmoothingMilliseconds = Int32(
        exactly: parameterSmoothingMilliseconds
      ),
      let nativeMaxSources = Int32(exactly: maxSources),
      nativeHrtfFrameSize > 0,
      nativeParameterSmoothingMilliseconds >= 0,
      nativeMaxSources > 0
    else {
      throw SpatialAudioException("Invalid native spatial-audio engine configuration")
    }
    let requested = [hrtfFrameSize, parameterSmoothingMilliseconds, maxSources]
    if engineHandle != 0 {
      guard requested == engineConfiguration else {
        throw SpatialAudioException(
          "Native spatial audio is already initialized with different settings"
        )
      }
      return capabilities()
    }
    var result: Int32 = nativeSuccess
    let handle = PACreateSpatialAudioEngine(
      nativeHrtfFrameSize,
      nativeParameterSmoothingMilliseconds,
      nativeMaxSources,
      &result
    )
    guard handle != 0, result == nativeSuccess else {
      throw SpatialAudioException("Native spatial-audio initialization failed (\(result))")
    }
    engineHandle = handle
    engineConfiguration = requested
    return capabilities()
  }

  private func capabilities() -> [String: Any] {
    [
      "available": engineHandle != 0,
      "hrtf": engineHandle != 0,
      "sampleRate": engineHandle == 0 ? 0 : PASpatialAudioEngineSampleRate(engineHandle)
    ]
  }

  private func validSourceID(_ sourceID: String) -> Bool {
    let range = NSRange(sourceID.startIndex..<sourceID.endIndex, in: sourceID)
    return sourceIDPattern.firstMatch(in: sourceID, range: range) != nil
  }

  private func validPath(_ path: String) -> Bool {
    !path.isEmpty && !path.utf8.contains(0)
  }

  private func createSource(
    sourceID: String,
    options: SpatialAudioSourceOptions
  ) throws -> [Double] {
    guard engineHandle != 0 else {
      throw SpatialAudioException("Native spatial audio is not initialized")
    }
    let hasStem = !options.loopPath.isEmpty
    let hasSequence = !options.sequencePaths.isEmpty
    guard
      validSourceID(sourceID),
      hasStem != hasSequence,
      options.loopPath.isEmpty || validPath(options.loopPath),
      options.introPath.map(validPath) ?? true,
      options.outroPath.map(validPath) ?? true,
      options.sequencePaths.count <= maxSequenceSegments,
      options.sequencePaths.allSatisfy(validPath),
      !hasSequence || options.sequenceNextStartRatios.count == options.sequencePaths.count,
      options.sequenceNextStartRatios.allSatisfy { $0.isFinite && $0 >= 0 && $0 <= 1 },
      !hasSequence || (
        options.introPath == nil &&
        options.outroPath == nil &&
        !options.playIntro &&
        !options.looping &&
        !options.streamFromDisk
      )
    else {
      throw SpatialAudioException("Invalid native spatial-audio source")
    }
    destroySource(sourceID)
    var result: Int32 = nativeSuccess
    let handle: UInt
    if hasSequence {
      handle = PACreateSpatialAudioSequenceSource(
        engineHandle,
        options.sequencePaths,
        options.sequenceNextStartRatios.map { NSNumber(value: $0) },
        options.startPaused,
        Float(options.volume),
        Float(options.pitch),
        Float(options.x),
        Float(options.y),
        Float(options.z),
        Float(options.spatialBlend),
        &result
      )
    } else {
      handle = options.loopPath.withCString { loopCString in
        let createWithIntro: (UnsafePointer<CChar>?) -> UInt = { introCString in
          let createWithOutro: (UnsafePointer<CChar>?) -> UInt = { outroCString in
            PACreateSpatialAudioSource(
              self.engineHandle,
              introCString,
              loopCString,
              outroCString,
              options.playIntro,
              options.looping,
              options.streamFromDisk,
              options.startPaused,
              Float(options.volume),
              Float(options.pitch),
              Float(options.x),
              Float(options.y),
              Float(options.z),
              Float(options.spatialBlend),
              &result
            )
          }
          if let outroPath = options.outroPath, !outroPath.isEmpty {
            return outroPath.withCString(createWithOutro)
          }
          return createWithOutro(nil)
        }
        if let introPath = options.introPath, !introPath.isEmpty {
          return introPath.withCString(createWithIntro)
        }
        return createWithIntro(nil)
      }
    }
    guard handle != 0, result == nativeSuccess else {
      throw SpatialAudioException("Native spatial-audio source creation failed (\(result))")
    }
    let durations: [Double]
    if hasSequence {
      let sampleRate = PASpatialAudioEngineSampleRate(engineHandle)
      let durationFrames = PASpatialAudioSourceSequenceDurations(handle)
      guard
        sampleRate > 0,
        durationFrames.count == options.sequencePaths.count,
        durationFrames.allSatisfy({ $0.uint64Value > 0 })
      else {
        PADestroySpatialAudioSource(handle)
        throw SpatialAudioException("Native spatial-audio sequence timing is invalid")
      }
      durations = durationFrames.map {
        Double(truncating: $0) * 1000 / Double(sampleRate)
      }
    } else {
      durations = []
    }
    sources[sourceID] = handle
    return durations
  }

  private func destroySource(_ sourceID: String) {
    guard let source = sources.removeValue(forKey: sourceID) else { return }
    PAStopSpatialAudioSource(source)
    PADestroySpatialAudioSource(source)
  }

  private func shutdown() {
    Array(sources.keys).forEach { destroySource($0) }
    if engineHandle != 0 {
      PADestroySpatialAudioEngine(engineHandle)
      engineHandle = 0
    }
    engineConfiguration = nil
  }
}
