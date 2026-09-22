/*
 * Stable C interface used by PlayAural's Expo module.
 *
 * Protocol interpretation, attenuation, automation, buses, ducking, and user
 * volume remain in the shared TypeScript mixer. This layer owns only native
 * playback, seamless stem scheduling, and Steam Audio binaural rendering.
 */

#ifndef COSMOS_MOBILE_H
#define COSMOS_MOBILE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct cosmos_mobile_engine cosmos_mobile_engine;
typedef struct cosmos_mobile_source cosmos_mobile_source;

typedef enum cosmos_mobile_result {
    COSMOS_MOBILE_SUCCESS = 0,
    COSMOS_MOBILE_INVALID_ARGUMENT = -1,
    COSMOS_MOBILE_OUT_OF_MEMORY = -2,
    COSMOS_MOBILE_ENGINE_INITIALIZATION_FAILED = -3,
    COSMOS_MOBILE_HRTF_INITIALIZATION_FAILED = -4,
    COSMOS_MOBILE_SOURCE_LIMIT_REACHED = -5,
    COSMOS_MOBILE_SOURCE_LOAD_FAILED = -6,
    COSMOS_MOBILE_GRAPH_INITIALIZATION_FAILED = -7,
    COSMOS_MOBILE_PLAYBACK_FAILED = -8,
    COSMOS_MOBILE_UNSUPPORTED_OPERATION = -9
} cosmos_mobile_result;

typedef struct cosmos_mobile_engine_config {
    uint32_t hrtf_frame_size;
    uint32_t parameter_smoothing_milliseconds;
    uint32_t max_sources;
} cosmos_mobile_engine_config;

typedef struct cosmos_mobile_source_config {
    const char* intro_path;
    const char* loop_path;
    const char* outro_path;
    int32_t play_intro;
    int32_t looping;
    int32_t stream_from_disk;
    int32_t start_paused;
    float volume;
    float pitch;
    float x;
    float y;
    float z;
    float spatial_blend;
    const char* const* sequence_paths;
    const float* sequence_next_start_ratios;
    uint32_t sequence_count;
} cosmos_mobile_source_config;

cosmos_mobile_engine* cosmos_mobile_engine_create(
    const cosmos_mobile_engine_config* config,
    cosmos_mobile_result* result
);
void cosmos_mobile_engine_destroy(cosmos_mobile_engine* engine);
uint32_t cosmos_mobile_engine_sample_rate(const cosmos_mobile_engine* engine);
uint32_t cosmos_mobile_engine_active_sources(const cosmos_mobile_engine* engine);

cosmos_mobile_source* cosmos_mobile_source_create(
    cosmos_mobile_engine* engine,
    const cosmos_mobile_source_config* config,
    cosmos_mobile_result* result
);
void cosmos_mobile_source_destroy(cosmos_mobile_source* source);

cosmos_mobile_result cosmos_mobile_source_set_parameters(
    cosmos_mobile_source* source,
    float volume,
    float pitch,
    float x,
    float y,
    float z,
    float spatial_blend
);
cosmos_mobile_result cosmos_mobile_source_set_sequence_segment_parameters(
    cosmos_mobile_source* source,
    uint32_t index,
    float gain,
    float x,
    float y,
    float z,
    float spatial_blend
);
cosmos_mobile_result cosmos_mobile_source_pause(cosmos_mobile_source* source);
cosmos_mobile_result cosmos_mobile_source_resume(cosmos_mobile_source* source);
cosmos_mobile_result cosmos_mobile_source_request_outro(
    cosmos_mobile_source* source,
    int32_t finish_loop_boundary
);
void cosmos_mobile_source_stop(cosmos_mobile_source* source);
int32_t cosmos_mobile_source_at_end(cosmos_mobile_source* source);
uint32_t cosmos_mobile_source_sequence_count(const cosmos_mobile_source* source);
uint64_t cosmos_mobile_source_sequence_duration_frames(
    const cosmos_mobile_source* source,
    uint32_t index
);

#ifdef __cplusplus
}
#endif

#endif
