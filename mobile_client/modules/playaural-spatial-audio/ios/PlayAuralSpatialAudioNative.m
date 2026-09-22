#import <TargetConditionals.h>

#include "cosmos_mobile.h"

#if TARGET_OS_SIMULATOR

cosmos_mobile_engine* cosmos_mobile_engine_create(
    const cosmos_mobile_engine_config* config,
    cosmos_mobile_result* result
) {
    (void)config;
    if (result != NULL) {
        *result = COSMOS_MOBILE_ENGINE_INITIALIZATION_FAILED;
    }
    return NULL;
}
void cosmos_mobile_engine_destroy(cosmos_mobile_engine* engine) { (void)engine; }
uint32_t cosmos_mobile_engine_sample_rate(const cosmos_mobile_engine* engine) {
    (void)engine;
    return 0;
}
uint32_t cosmos_mobile_engine_active_sources(const cosmos_mobile_engine* engine) {
    (void)engine;
    return 0;
}
cosmos_mobile_source* cosmos_mobile_source_create(
    cosmos_mobile_engine* engine,
    const cosmos_mobile_source_config* config,
    cosmos_mobile_result* result
) {
    (void)engine;
    (void)config;
    if (result != NULL) {
        *result = COSMOS_MOBILE_ENGINE_INITIALIZATION_FAILED;
    }
    return NULL;
}
void cosmos_mobile_source_destroy(cosmos_mobile_source* source) { (void)source; }
cosmos_mobile_result cosmos_mobile_source_set_parameters(
    cosmos_mobile_source* source,
    float volume,
    float pitch,
    float x,
    float y,
    float z,
    float spatial_blend
) {
    (void)source;
    (void)volume;
    (void)pitch;
    (void)x;
    (void)y;
    (void)z;
    (void)spatial_blend;
    return COSMOS_MOBILE_UNSUPPORTED_OPERATION;
}
cosmos_mobile_result cosmos_mobile_source_set_sequence_segment_parameters(
    cosmos_mobile_source* source,
    uint32_t index,
    float gain,
    float x,
    float y,
    float z,
    float spatial_blend
) {
    (void)source;
    (void)index;
    (void)gain;
    (void)x;
    (void)y;
    (void)z;
    (void)spatial_blend;
    return COSMOS_MOBILE_UNSUPPORTED_OPERATION;
}
cosmos_mobile_result cosmos_mobile_source_pause(cosmos_mobile_source* source) {
    (void)source;
    return COSMOS_MOBILE_UNSUPPORTED_OPERATION;
}
cosmos_mobile_result cosmos_mobile_source_resume(cosmos_mobile_source* source) {
    (void)source;
    return COSMOS_MOBILE_UNSUPPORTED_OPERATION;
}
cosmos_mobile_result cosmos_mobile_source_request_outro(
    cosmos_mobile_source* source,
    int32_t finish_loop_boundary
) {
    (void)source;
    (void)finish_loop_boundary;
    return COSMOS_MOBILE_UNSUPPORTED_OPERATION;
}
void cosmos_mobile_source_stop(cosmos_mobile_source* source) { (void)source; }
int32_t cosmos_mobile_source_at_end(cosmos_mobile_source* source) {
    (void)source;
    return 1;
}
uint32_t cosmos_mobile_source_sequence_count(const cosmos_mobile_source* source) {
    (void)source;
    return 0;
}
uint64_t cosmos_mobile_source_sequence_duration_frames(
    const cosmos_mobile_source* source,
    uint32_t index
) {
    (void)source;
    (void)index;
    return 0;
}

#else

#define MA_NO_WEBAUDIO
#define MA_NO_NULL
#include "miniaudio_impl.c"
#include "miniaudio_phonon.c"
#include "cosmos_mobile.c"

#endif
