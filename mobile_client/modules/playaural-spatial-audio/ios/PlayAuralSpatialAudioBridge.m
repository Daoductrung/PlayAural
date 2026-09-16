#import "PlayAuralSpatialAudioBridge.h"

#include "cosmos_mobile.h"

uintptr_t PACreateSpatialAudioEngine(
    int32_t hrtfFrameSize,
    int32_t parameterSmoothingMilliseconds,
    int32_t maxSources,
    int32_t* result
) {
    cosmos_mobile_engine_config config;
    cosmos_mobile_result nativeResult;
    cosmos_mobile_engine* engine;
    config.hrtf_frame_size = (uint32_t)hrtfFrameSize;
    config.parameter_smoothing_milliseconds = (uint32_t)parameterSmoothingMilliseconds;
    config.max_sources = (uint32_t)maxSources;
    engine = cosmos_mobile_engine_create(&config, &nativeResult);
    if (result != NULL) {
        *result = (int32_t)nativeResult;
    }
    return (uintptr_t)engine;
}

void PADestroySpatialAudioEngine(uintptr_t engineHandle) {
    cosmos_mobile_engine_destroy((cosmos_mobile_engine*)engineHandle);
}

int32_t PASpatialAudioEngineSampleRate(uintptr_t engineHandle) {
    return (int32_t)cosmos_mobile_engine_sample_rate(
        (cosmos_mobile_engine*)engineHandle
    );
}

uintptr_t PACreateSpatialAudioSource(
    uintptr_t engineHandle,
    const char* introPath,
    const char* loopPath,
    const char* outroPath,
    BOOL playIntro,
    BOOL looping,
    BOOL streamFromDisk,
    BOOL startPaused,
    float volume,
    float pitch,
    float x,
    float y,
    float z,
    float spatialBlend,
    int32_t* result
) {
    cosmos_mobile_source_config config;
    cosmos_mobile_result nativeResult;
    cosmos_mobile_source* source;
    config.intro_path = introPath;
    config.loop_path = loopPath;
    config.outro_path = outroPath;
    config.play_intro = playIntro ? 1 : 0;
    config.looping = looping ? 1 : 0;
    config.stream_from_disk = streamFromDisk ? 1 : 0;
    config.start_paused = startPaused ? 1 : 0;
    config.volume = volume;
    config.pitch = pitch;
    config.x = x;
    config.y = y;
    config.z = z;
    config.spatial_blend = spatialBlend;
    source = cosmos_mobile_source_create(
        (cosmos_mobile_engine*)engineHandle,
        &config,
        &nativeResult
    );
    if (result != NULL) {
        *result = (int32_t)nativeResult;
    }
    return (uintptr_t)source;
}

void PADestroySpatialAudioSource(uintptr_t sourceHandle) {
    cosmos_mobile_source_destroy((cosmos_mobile_source*)sourceHandle);
}

int32_t PASetSpatialAudioSourceParameters(
    uintptr_t sourceHandle,
    float volume,
    float pitch,
    float x,
    float y,
    float z,
    float spatialBlend
) {
    return (int32_t)cosmos_mobile_source_set_parameters(
        (cosmos_mobile_source*)sourceHandle,
        volume,
        pitch,
        x,
        y,
        z,
        spatialBlend
    );
}

int32_t PAPauseSpatialAudioSource(uintptr_t sourceHandle) {
    return (int32_t)cosmos_mobile_source_pause(
        (cosmos_mobile_source*)sourceHandle
    );
}

int32_t PAResumeSpatialAudioSource(uintptr_t sourceHandle) {
    return (int32_t)cosmos_mobile_source_resume(
        (cosmos_mobile_source*)sourceHandle
    );
}

int32_t PARequestSpatialAudioSourceOutro(
    uintptr_t sourceHandle,
    BOOL finishLoopBoundary
) {
    return (int32_t)cosmos_mobile_source_request_outro(
        (cosmos_mobile_source*)sourceHandle,
        finishLoopBoundary ? 1 : 0
    );
}

void PAStopSpatialAudioSource(uintptr_t sourceHandle) {
    cosmos_mobile_source_stop((cosmos_mobile_source*)sourceHandle);
}

BOOL PASpatialAudioSourceAtEnd(uintptr_t sourceHandle) {
    return cosmos_mobile_source_at_end(
        (cosmos_mobile_source*)sourceHandle
    ) ? YES : NO;
}
