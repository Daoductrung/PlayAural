#import <Foundation/Foundation.h>
#include <stdint.h>

NS_ASSUME_NONNULL_BEGIN

uintptr_t PACreateSpatialAudioEngine(
    int32_t hrtfFrameSize,
    int32_t parameterSmoothingMilliseconds,
    int32_t maxSources,
    int32_t* result
);
void PADestroySpatialAudioEngine(uintptr_t engineHandle);
int32_t PASpatialAudioEngineSampleRate(uintptr_t engineHandle);

uintptr_t PACreateSpatialAudioSource(
    uintptr_t engineHandle,
    const char* _Nullable introPath,
    const char* loopPath,
    const char* _Nullable outroPath,
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
);
uintptr_t PACreateSpatialAudioSequenceSource(
    uintptr_t engineHandle,
    NSArray<NSString*>* sequencePaths,
    NSArray<NSNumber*>* sequenceNextStartRatios,
    BOOL startPaused,
    float volume,
    float pitch,
    float x,
    float y,
    float z,
    float spatialBlend,
    int32_t* result
);
NSArray<NSNumber*>* PASpatialAudioSourceSequenceDurations(
    uintptr_t sourceHandle
);
void PADestroySpatialAudioSource(uintptr_t sourceHandle);
int32_t PASetSpatialAudioSourceParameters(
    uintptr_t sourceHandle,
    float volume,
    float pitch,
    float x,
    float y,
    float z,
    float spatialBlend
);
int32_t PAPauseSpatialAudioSource(uintptr_t sourceHandle);
int32_t PAResumeSpatialAudioSource(uintptr_t sourceHandle);
int32_t PARequestSpatialAudioSourceOutro(
    uintptr_t sourceHandle,
    BOOL finishLoopBoundary
);
void PAStopSpatialAudioSource(uintptr_t sourceHandle);
BOOL PASpatialAudioSourceAtEnd(uintptr_t sourceHandle);

NS_ASSUME_NONNULL_END
