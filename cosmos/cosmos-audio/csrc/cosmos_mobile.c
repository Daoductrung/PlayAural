#include "cosmos_mobile.h"

#include <float.h>
#include <math.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "miniaudio.h"
#include "miniaudio_phonon.h"

#define COSMOS_MOBILE_MAX_SEQUENCE_SEGMENTS 32

typedef struct cosmos_mobile_segment {
    ma_sound sound;
    ma_bool32 initialized;
    ma_uint64 length_frames;
    ma_uint32 sample_rate;
    ma_uint64 start_frame;
    float next_start_ratio;
} cosmos_mobile_segment;

struct cosmos_mobile_engine {
    ma_engine* engine;
    uint32_t hrtf_frame_size;
    uint32_t max_sources;
    uint32_t active_sources;
    ma_bool32 phonon_initialized;
    cosmos_mobile_source* first_source;
};

struct cosmos_mobile_source {
    cosmos_mobile_engine* owner;
    cosmos_mobile_source* previous;
    cosmos_mobile_source* next;
    ma_sound_group group;
    ma_bool32 group_initialized;
    ma_phonon_binaural_node* binaural_node;
    ma_bool32 binaural_node_initialized;
    cosmos_mobile_segment intro;
    cosmos_mobile_segment loop;
    cosmos_mobile_segment outro;
    cosmos_mobile_segment* sequence;
    ma_uint32 sequence_count;
    ma_bool32 looping;
    ma_bool32 linked;
    ma_bool32 started;
    ma_bool32 paused;
    ma_bool32 stopped;
    ma_bool32 outro_scheduled;
    ma_bool32 outro_requested;
    float pitch;
    ma_uint64 end_observation_deadline;
};

extern ma_engine* ma_engine_alloc(void);
extern void ma_engine_free(ma_engine* engine);
extern ma_result ma_engine_init_mobile_with_caching(
    ma_engine* engine,
    ma_uint32 period_size_in_frames,
    ma_uint32 parameter_smoothing_milliseconds
);
extern void ma_engine_uninit_with_caching(ma_engine* engine);
extern ma_node* ma_sound_get_node_ptr(ma_sound* sound);

static void set_result(cosmos_mobile_result* destination, cosmos_mobile_result value) {
    if (destination != NULL) {
        *destination = value;
    }
}

static ma_bool32 add_frames(
    ma_uint64 left,
    ma_uint64 right,
    ma_uint64* result
) {
    if (result == NULL || right > UINT64_MAX - left) {
        return MA_FALSE;
    }
    *result = left + right;
    return MA_TRUE;
}

static ma_bool32 pitched_frame_duration(
    ma_uint64 source_frames,
    ma_uint64 repetitions,
    ma_uint32 source_sample_rate,
    ma_uint32 engine_sample_rate,
    float pitch,
    ma_uint64* result
) {
    long double duration;
    if (
        result == NULL
        || source_frames == 0
        || repetitions == 0
        || source_sample_rate == 0
        || engine_sample_rate == 0
        || !isfinite(pitch)
        || pitch <= 0.0f
    ) {
        return MA_FALSE;
    }
    duration = ceill(
        (
            (long double)source_frames
            * (long double)repetitions
            * (long double)engine_sample_rate
        )
        / ((long double)source_sample_rate * (long double)pitch)
    );
    if (duration < 1.0L || duration > (long double)UINT64_MAX) {
        return MA_FALSE;
    }
    *result = (ma_uint64)duration;
    return MA_TRUE;
}

static ma_bool32 ratio_frame_duration(
    ma_uint64 frames,
    float ratio,
    ma_uint64* result
) {
    long double duration;
    if (
        result == NULL
        || !isfinite(ratio)
        || ratio < 0.0f
        || ratio > 1.0f
    ) {
        return MA_FALSE;
    }
    duration = ceill((long double)frames * (long double)ratio);
    if (duration < 0.0L || duration > (long double)UINT64_MAX) {
        return MA_FALSE;
    }
    *result = (ma_uint64)duration;
    return MA_TRUE;
}

static ma_bool32 valid_source_config(const cosmos_mobile_source_config* config) {
    ma_uint32 index;
    ma_bool32 has_stem;
    ma_bool32 has_sequence;
    if (config == NULL) {
        return MA_FALSE;
    }
    has_stem = config->loop_path != NULL && config->loop_path[0] != '\0';
    has_sequence = config->sequence_paths != NULL && config->sequence_count > 0;
    if (
        has_stem == has_sequence
        || (config->sequence_paths == NULL) != (config->sequence_count == 0)
        || (config->sequence_next_start_ratios == NULL) != (config->sequence_count == 0)
        || config->sequence_count > COSMOS_MOBILE_MAX_SEQUENCE_SEGMENTS
        || (has_sequence && (
            config->intro_path != NULL
            || config->outro_path != NULL
            || config->play_intro
            || config->looping
        ))
    ) {
        return MA_FALSE;
    }
    for (index = 0; has_sequence && index < config->sequence_count; index += 1) {
        if (
            config->sequence_paths[index] == NULL
            || config->sequence_paths[index][0] == '\0'
            || !isfinite(config->sequence_next_start_ratios[index])
            || config->sequence_next_start_ratios[index] < 0.0f
            || config->sequence_next_start_ratios[index] > 1.0f
        ) {
            return MA_FALSE;
        }
    }
    return (config->play_intro == 0 || config->play_intro == 1)
        && (config->looping == 0 || config->looping == 1)
        && (config->stream_from_disk == 0 || config->stream_from_disk == 1)
        && (config->start_paused == 0 || config->start_paused == 1)
        && isfinite(config->volume)
        && config->volume >= 0.0f
        && config->volume <= 1.0f
        && isfinite(config->pitch)
        && config->pitch > 0.0f
        && config->pitch <= 4.0f
        && isfinite(config->x)
        && isfinite(config->y)
        && isfinite(config->z)
        && isfinite(config->spatial_blend)
        && config->spatial_blend >= 0.0f
        && config->spatial_blend <= 1.0f;
}

static void segment_uninit(cosmos_mobile_segment* segment) {
    if (segment->initialized) {
        ma_sound_stop(&segment->sound);
        ma_sound_uninit(&segment->sound);
        segment->initialized = MA_FALSE;
    }
}

static cosmos_mobile_result segment_init(
    cosmos_mobile_engine* owner,
    cosmos_mobile_source* source,
    cosmos_mobile_segment* segment,
    const char* path,
    ma_bool32 stream_from_disk
) {
    ma_result result;
    ma_uint32 flags;

    if (path == NULL || path[0] == '\0') {
        return COSMOS_MOBILE_SUCCESS;
    }
    flags = MA_SOUND_FLAG_NO_SPATIALIZATION
        | (stream_from_disk ? MA_SOUND_FLAG_STREAM : MA_SOUND_FLAG_DECODE);
    result = ma_sound_init_from_file(
        owner->engine,
        path,
        flags,
        &source->group,
        NULL,
        &segment->sound
    );
    if (result != MA_SUCCESS) {
        return COSMOS_MOBILE_SOURCE_LOAD_FAILED;
    }
    segment->initialized = MA_TRUE;
    result = ma_sound_get_length_in_pcm_frames(&segment->sound, &segment->length_frames);
    if (result == MA_SUCCESS) {
        result = ma_sound_get_data_format(
            &segment->sound,
            NULL,
            NULL,
            &segment->sample_rate,
            NULL,
            0
        );
    }
    if (
        result != MA_SUCCESS
        || segment->length_frames == 0
        || segment->sample_rate == 0
    ) {
        segment_uninit(segment);
        return COSMOS_MOBILE_SOURCE_LOAD_FAILED;
    }
    return COSMOS_MOBILE_SUCCESS;
}

static cosmos_mobile_result segment_schedule(
    cosmos_mobile_segment* segment,
    ma_uint64 start_frame,
    ma_bool32 looping
) {
    ma_result result;
    if (!segment->initialized) {
        return COSMOS_MOBILE_INVALID_ARGUMENT;
    }
    segment->start_frame = start_frame;
    ma_sound_set_looping(&segment->sound, looping);
    ma_sound_set_start_time_in_pcm_frames(&segment->sound, start_frame);
    result = ma_sound_start(&segment->sound);
    return result == MA_SUCCESS
        ? COSMOS_MOBILE_SUCCESS
        : COSMOS_MOBILE_PLAYBACK_FAILED;
}

static cosmos_mobile_result source_schedule_initial(cosmos_mobile_source* source) {
    cosmos_mobile_result result;
    ma_uint64 first_frame;
    ma_uint64 loop_start_frame;
    ma_uint64 outro_start_frame;
    ma_uint64 segment_duration;
    ma_uint64 next_start_offset;
    ma_uint64 sequence_cursor;
    ma_uint32 sequence_index;

    if (
        source == NULL
        || source->owner == NULL
        || source->started
        || (!source->loop.initialized && source->sequence_count == 0)
    ) {
        return COSMOS_MOBILE_INVALID_ARGUMENT;
    }
    if (!add_frames(
        ma_engine_get_time_in_pcm_frames(source->owner->engine),
        source->owner->hrtf_frame_size,
        &first_frame
    )) {
        return COSMOS_MOBILE_PLAYBACK_FAILED;
    }
    if (source->sequence_count > 0) {
        sequence_cursor = first_frame;
        for (sequence_index = 0; sequence_index < source->sequence_count; sequence_index += 1) {
            cosmos_mobile_segment* sequence_segment = &source->sequence[sequence_index];
            result = segment_schedule(sequence_segment, sequence_cursor, MA_FALSE);
            if (
                result != COSMOS_MOBILE_SUCCESS
                || !pitched_frame_duration(
                    sequence_segment->length_frames,
                    1,
                    sequence_segment->sample_rate,
                    ma_engine_get_sample_rate(source->owner->engine),
                    source->pitch,
                    &segment_duration
                )
                || !ratio_frame_duration(
                    segment_duration,
                    sequence_segment->next_start_ratio,
                    &next_start_offset
                )
                || !add_frames(sequence_cursor, next_start_offset, &sequence_cursor)
            ) {
                return result == COSMOS_MOBILE_SUCCESS
                    ? COSMOS_MOBILE_PLAYBACK_FAILED
                    : result;
            }
        }
        source->started = MA_TRUE;
        ma_node_set_state((ma_node*)source->binaural_node, ma_node_state_started);
        return COSMOS_MOBILE_SUCCESS;
    }
    loop_start_frame = first_frame;
    if (source->intro.initialized) {
        result = segment_schedule(&source->intro, first_frame, MA_FALSE);
        if (result != COSMOS_MOBILE_SUCCESS) {
            return result;
        }
        if (
            !pitched_frame_duration(
                source->intro.length_frames,
                1,
                source->intro.sample_rate,
                ma_engine_get_sample_rate(source->owner->engine),
                source->pitch,
                &segment_duration
            )
            || !add_frames(
                loop_start_frame,
                segment_duration,
                &loop_start_frame
            )
        ) {
            return COSMOS_MOBILE_PLAYBACK_FAILED;
        }
    }
    result = segment_schedule(&source->loop, loop_start_frame, source->looping);
    if (result != COSMOS_MOBILE_SUCCESS) {
        return result;
    }
    if (!source->looping && source->outro.initialized) {
        if (
            !pitched_frame_duration(
                source->loop.length_frames,
                1,
                source->loop.sample_rate,
                ma_engine_get_sample_rate(source->owner->engine),
                source->pitch,
                &segment_duration
            )
            || !add_frames(
                loop_start_frame,
                segment_duration,
                &outro_start_frame
            )
        ) {
            return COSMOS_MOBILE_PLAYBACK_FAILED;
        }
        result = segment_schedule(
            &source->outro,
            outro_start_frame,
            MA_FALSE
        );
        if (result != COSMOS_MOBILE_SUCCESS) {
            return result;
        }
        source->outro_scheduled = MA_TRUE;
    }
    source->started = MA_TRUE;
    ma_node_set_state((ma_node*)source->binaural_node, ma_node_state_started);
    return COSMOS_MOBILE_SUCCESS;
}

static void source_unlink(cosmos_mobile_source* source) {
    cosmos_mobile_engine* owner;
    if (source == NULL || source->owner == NULL || !source->linked) {
        return;
    }
    owner = source->owner;
    if (source->previous != NULL) {
        source->previous->next = source->next;
    } else if (owner->first_source == source) {
        owner->first_source = source->next;
    }
    if (source->next != NULL) {
        source->next->previous = source->previous;
    }
    if (owner->active_sources > 0) {
        owner->active_sources -= 1;
    }
    source->owner = NULL;
    source->linked = MA_FALSE;
    source->previous = NULL;
    source->next = NULL;
}

cosmos_mobile_engine* cosmos_mobile_engine_create(
    const cosmos_mobile_engine_config* config,
    cosmos_mobile_result* result
) {
    cosmos_mobile_engine* mobile_engine;
    ma_result native_result;
    ma_uint32 sample_rate;

    set_result(result, COSMOS_MOBILE_INVALID_ARGUMENT);
    if (
        config == NULL
        || config->hrtf_frame_size == 0
        || config->max_sources == 0
    ) {
        return NULL;
    }
    mobile_engine = (cosmos_mobile_engine*)calloc(1, sizeof(*mobile_engine));
    if (mobile_engine == NULL) {
        set_result(result, COSMOS_MOBILE_OUT_OF_MEMORY);
        return NULL;
    }
    mobile_engine->engine = ma_engine_alloc();
    if (mobile_engine->engine == NULL) {
        free(mobile_engine);
        set_result(result, COSMOS_MOBILE_OUT_OF_MEMORY);
        return NULL;
    }
    native_result = ma_engine_init_mobile_with_caching(
        mobile_engine->engine,
        config->hrtf_frame_size,
        config->parameter_smoothing_milliseconds
    );
    if (native_result != MA_SUCCESS) {
        ma_engine_free(mobile_engine->engine);
        free(mobile_engine);
        set_result(result, COSMOS_MOBILE_ENGINE_INITIALIZATION_FAILED);
        return NULL;
    }
    sample_rate = ma_engine_get_sample_rate(mobile_engine->engine);
    native_result = ma_phonon_init(sample_rate, config->hrtf_frame_size);
    if (native_result != MA_SUCCESS) {
        ma_engine_uninit_with_caching(mobile_engine->engine);
        ma_engine_free(mobile_engine->engine);
        free(mobile_engine);
        set_result(result, COSMOS_MOBILE_HRTF_INITIALIZATION_FAILED);
        return NULL;
    }
    mobile_engine->phonon_initialized = MA_TRUE;
    mobile_engine->hrtf_frame_size = config->hrtf_frame_size;
    mobile_engine->max_sources = config->max_sources;
    set_result(result, COSMOS_MOBILE_SUCCESS);
    return mobile_engine;
}

void cosmos_mobile_engine_destroy(cosmos_mobile_engine* engine) {
    if (engine == NULL) {
        return;
    }
    while (engine->first_source != NULL) {
        cosmos_mobile_source_destroy(engine->first_source);
    }
    if (engine->phonon_initialized) {
        ma_phonon_uninit();
        engine->phonon_initialized = MA_FALSE;
    }
    if (engine->engine != NULL) {
        ma_engine_uninit_with_caching(engine->engine);
        ma_engine_free(engine->engine);
        engine->engine = NULL;
    }
    free(engine);
}

uint32_t cosmos_mobile_engine_sample_rate(const cosmos_mobile_engine* engine) {
    return engine != NULL && engine->engine != NULL
        ? ma_engine_get_sample_rate(engine->engine)
        : 0;
}

uint32_t cosmos_mobile_engine_active_sources(const cosmos_mobile_engine* engine) {
    return engine != NULL ? engine->active_sources : 0;
}

cosmos_mobile_source* cosmos_mobile_source_create(
    cosmos_mobile_engine* engine,
    const cosmos_mobile_source_config* config,
    cosmos_mobile_result* result
) {
    cosmos_mobile_source* source;
    cosmos_mobile_result source_result;
    ma_result native_result;
    ma_bool32 stream_from_disk;
    ma_phonon_binaural_node_config binaural_config;
    ma_node* group_node;
    ma_uint32 sequence_index;

    set_result(result, COSMOS_MOBILE_INVALID_ARGUMENT);
    if (engine == NULL || engine->engine == NULL || !valid_source_config(config)) {
        return NULL;
    }
    if (engine->active_sources >= engine->max_sources) {
        set_result(result, COSMOS_MOBILE_SOURCE_LIMIT_REACHED);
        return NULL;
    }
    source = (cosmos_mobile_source*)calloc(1, sizeof(*source));
    if (source == NULL) {
        set_result(result, COSMOS_MOBILE_OUT_OF_MEMORY);
        return NULL;
    }
    source->owner = engine;
    source->sequence_count = config->sequence_count;
    stream_from_disk = config->stream_from_disk ? MA_TRUE : MA_FALSE;

    native_result = ma_sound_group_init(engine->engine, 0, NULL, &source->group);
    if (native_result != MA_SUCCESS) {
        source_result = COSMOS_MOBILE_GRAPH_INITIALIZATION_FAILED;
        goto on_error;
    }
    source->group_initialized = MA_TRUE;
    ma_sound_group_set_spatialization_enabled(&source->group, MA_FALSE);

    source->binaural_node = ma_phonon_binaural_node_alloc();
    if (source->binaural_node == NULL) {
        source_result = COSMOS_MOBILE_OUT_OF_MEMORY;
        goto on_error;
    }
    binaural_config = ma_phonon_binaural_node_config_init(
        2,
        ma_phonon_get_audio_settings(),
        ma_phonon_get_context(),
        ma_phonon_get_hrtf()
    );
    native_result = ma_phonon_binaural_node_init_with_tail_processing(
        ma_engine_get_node_graph(engine->engine),
        &binaural_config,
        NULL,
        source->binaural_node
    );
    if (native_result != MA_SUCCESS) {
        source_result = COSMOS_MOBILE_GRAPH_INITIALIZATION_FAILED;
        goto on_error;
    }
    source->binaural_node_initialized = MA_TRUE;
    ma_node_set_state((ma_node*)source->binaural_node, ma_node_state_stopped);
    group_node = ma_sound_get_node_ptr(&source->group);
    if (
        group_node == NULL
        || ma_node_detach_output_bus(group_node, 0) != MA_SUCCESS
        || ma_node_attach_output_bus(
            group_node,
            0,
            (ma_node*)source->binaural_node,
            0
        ) != MA_SUCCESS
        || ma_node_attach_output_bus(
            (ma_node*)source->binaural_node,
            0,
            ma_engine_get_endpoint(engine->engine),
            0
        ) != MA_SUCCESS
    ) {
        source_result = COSMOS_MOBILE_GRAPH_INITIALIZATION_FAILED;
        goto on_error;
    }

    if (source->sequence_count > 0) {
        source->sequence = (cosmos_mobile_segment*)calloc(
            source->sequence_count,
            sizeof(*source->sequence)
        );
        if (source->sequence == NULL) {
            source_result = COSMOS_MOBILE_OUT_OF_MEMORY;
            goto on_error;
        }
        for (sequence_index = 0; sequence_index < source->sequence_count; sequence_index += 1) {
            source->sequence[sequence_index].next_start_ratio =
                config->sequence_next_start_ratios[sequence_index];
            source_result = segment_init(
                engine,
                source,
                &source->sequence[sequence_index],
                config->sequence_paths[sequence_index],
                stream_from_disk
            );
            if (source_result != COSMOS_MOBILE_SUCCESS) {
                goto on_error;
            }
        }
    } else if (config->play_intro && config->intro_path != NULL && config->intro_path[0] != '\0') {
        source_result = segment_init(
            engine,
            source,
            &source->intro,
            config->intro_path,
            stream_from_disk
        );
        if (source_result != COSMOS_MOBILE_SUCCESS) {
            goto on_error;
        }
    }
    if (source->sequence_count == 0) {
        source_result = segment_init(
            engine,
            source,
            &source->loop,
            config->loop_path,
            stream_from_disk
        );
        if (source_result != COSMOS_MOBILE_SUCCESS) {
            goto on_error;
        }
        source_result = segment_init(
            engine,
            source,
            &source->outro,
            config->outro_path,
            stream_from_disk
        );
        if (source_result != COSMOS_MOBILE_SUCCESS) {
            goto on_error;
        }
    }

    source_result = cosmos_mobile_source_set_parameters(
        source,
        config->volume,
        config->pitch,
        config->x,
        config->y,
        config->z,
        config->spatial_blend
    );
    if (source_result != COSMOS_MOBILE_SUCCESS) {
        goto on_error;
    }
    source->looping = config->looping ? MA_TRUE : MA_FALSE;
    if (config->start_paused) {
        if (ma_sound_group_stop(&source->group) != MA_SUCCESS) {
            source_result = COSMOS_MOBILE_PLAYBACK_FAILED;
            goto on_error;
        }
        source->paused = MA_TRUE;
    } else {
        source_result = source_schedule_initial(source);
        if (source_result != COSMOS_MOBILE_SUCCESS) {
            goto on_error;
        }
    }

    source->next = engine->first_source;
    if (source->next != NULL) {
        source->next->previous = source;
    }
    engine->first_source = source;
    engine->active_sources += 1;
    source->linked = MA_TRUE;
    set_result(result, COSMOS_MOBILE_SUCCESS);
    return source;

on_error:
    cosmos_mobile_source_destroy(source);
    set_result(result, source_result);
    return NULL;
}

void cosmos_mobile_source_destroy(cosmos_mobile_source* source) {
    ma_node* group_node;
    ma_uint32 sequence_index;
    if (source == NULL) {
        return;
    }
    source_unlink(source);
    segment_uninit(&source->intro);
    segment_uninit(&source->loop);
    segment_uninit(&source->outro);
    if (source->sequence != NULL) {
        for (sequence_index = 0; sequence_index < source->sequence_count; sequence_index += 1) {
            segment_uninit(&source->sequence[sequence_index]);
        }
    }
    free(source->sequence);
    source->sequence = NULL;
    source->sequence_count = 0;
    if (source->group_initialized) {
        group_node = ma_sound_get_node_ptr(&source->group);
        if (group_node != NULL) {
            ma_node_detach_output_bus(group_node, 0);
        }
    }
    if (source->binaural_node_initialized) {
        ma_phonon_binaural_node_uninit(source->binaural_node, NULL);
        source->binaural_node_initialized = MA_FALSE;
    }
    if (source->binaural_node != NULL) {
        ma_phonon_binaural_node_free(source->binaural_node);
        source->binaural_node = NULL;
    }
    if (source->group_initialized) {
        ma_sound_group_uninit(&source->group);
        source->group_initialized = MA_FALSE;
    }
    free(source);
}

cosmos_mobile_result cosmos_mobile_source_set_parameters(
    cosmos_mobile_source* source,
    float volume,
    float pitch,
    float x,
    float y,
    float z,
    float spatial_blend
) {
    float length;
    float steam_x;
    float steam_y;
    float steam_z;

    if (
        source == NULL
        || !source->group_initialized
        || !source->binaural_node_initialized
        || source->stopped
        || !isfinite(volume)
        || !isfinite(pitch)
        || !isfinite(x)
        || !isfinite(y)
        || !isfinite(z)
        || !isfinite(spatial_blend)
        || volume < 0.0f
        || volume > 1.0f
        || pitch <= 0.0f
        || pitch > 4.0f
        || spatial_blend < 0.0f
        || spatial_blend > 1.0f
    ) {
        return COSMOS_MOBILE_INVALID_ARGUMENT;
    }
    /* Stem boundaries are scheduled on the absolute engine timeline. Changing
     * pitch after playback starts would invalidate those seamless boundaries. */
    if (source->started && source->pitch != pitch) {
        return COSMOS_MOBILE_UNSUPPORTED_OPERATION;
    }

    ma_sound_group_set_volume(&source->group, volume);
    ma_sound_group_set_pitch(&source->group, pitch);
    source->pitch = pitch;
    length = hypotf(hypotf(x, y), z);
    if (length <= FLT_EPSILON) {
        steam_x = 0.0f;
        steam_y = 0.0f;
        steam_z = -1.0f;
        spatial_blend = 0.0f;
    } else {
        steam_x = x / length;
        steam_y = z / length;
        steam_z = -y / length;
    }
    return ma_phonon_binaural_node_set_parameters(
        source->binaural_node,
        steam_x,
        steam_y,
        steam_z,
        spatial_blend,
        IPL_HRTFINTERPOLATION_BILINEAR
    ) == MA_SUCCESS
        ? COSMOS_MOBILE_SUCCESS
        : COSMOS_MOBILE_INVALID_ARGUMENT;
}

cosmos_mobile_result cosmos_mobile_source_pause(cosmos_mobile_source* source) {
    if (source == NULL || !source->group_initialized || source->stopped) {
        return COSMOS_MOBILE_INVALID_ARGUMENT;
    }
    if (source->paused) {
        return COSMOS_MOBILE_SUCCESS;
    }
    if (
        source->intro.initialized
        || source->outro.initialized
        || source->sequence_count > 0
    ) {
        return COSMOS_MOBILE_UNSUPPORTED_OPERATION;
    }
    if (ma_sound_group_stop(&source->group) != MA_SUCCESS) {
        return COSMOS_MOBILE_PLAYBACK_FAILED;
    }
    ma_node_set_state((ma_node*)source->binaural_node, ma_node_state_stopped);
    source->paused = MA_TRUE;
    return COSMOS_MOBILE_SUCCESS;
}

cosmos_mobile_result cosmos_mobile_source_resume(cosmos_mobile_source* source) {
    if (source == NULL || !source->group_initialized || source->stopped) {
        return COSMOS_MOBILE_INVALID_ARGUMENT;
    }
    if (source->paused) {
        if (!source->started) {
            cosmos_mobile_result result = source_schedule_initial(source);
            if (result != COSMOS_MOBILE_SUCCESS) {
                return result;
            }
        }
        ma_node_set_state((ma_node*)source->binaural_node, ma_node_state_started);
        if (ma_sound_group_start(&source->group) != MA_SUCCESS) {
            ma_node_set_state((ma_node*)source->binaural_node, ma_node_state_stopped);
            return COSMOS_MOBILE_PLAYBACK_FAILED;
        }
        source->paused = MA_FALSE;
    }
    return COSMOS_MOBILE_SUCCESS;
}

cosmos_mobile_result cosmos_mobile_source_request_outro(
    cosmos_mobile_source* source,
    int32_t finish_loop_boundary
) {
    ma_uint64 now;
    ma_uint64 transition_frame;
    ma_uint64 earliest_transition_frame;
    ma_uint64 elapsed;
    ma_uint64 completed_cycles;
    ma_uint64 completed_loop_frames;
    ma_uint32 engine_sample_rate;
    long double required_cycles;
    cosmos_mobile_result result;

    if (
        source == NULL
        || source->owner == NULL
        || !source->started
        || !source->outro.initialized
        || source->stopped
        || (finish_loop_boundary != 0 && finish_loop_boundary != 1)
    ) {
        return COSMOS_MOBILE_INVALID_ARGUMENT;
    }
    if (source->outro_requested) {
        return COSMOS_MOBILE_SUCCESS;
    }
    now = ma_engine_get_time_in_pcm_frames(source->owner->engine);
    engine_sample_rate = ma_engine_get_sample_rate(source->owner->engine);
    if (engine_sample_rate == 0 || source->loop.sample_rate == 0) {
        return COSMOS_MOBILE_PLAYBACK_FAILED;
    }
    if (!add_frames(
        now,
        source->owner->hrtf_frame_size,
        &transition_frame
    )) {
        return COSMOS_MOBILE_PLAYBACK_FAILED;
    }
    earliest_transition_frame = transition_frame;
    if (finish_loop_boundary) {
        if (transition_frame < source->loop.start_frame) {
            if (
                !pitched_frame_duration(
                    source->loop.length_frames,
                    1,
                    source->loop.sample_rate,
                    engine_sample_rate,
                    source->pitch,
                    &completed_loop_frames
                )
                || !add_frames(
                    source->loop.start_frame,
                    completed_loop_frames,
                    &transition_frame
                )
            ) {
                return COSMOS_MOBILE_PLAYBACK_FAILED;
            }
        } else {
            elapsed = transition_frame - source->loop.start_frame;
            required_cycles = ceill(
                (
                    (long double)elapsed
                    * (long double)source->pitch
                    * (long double)source->loop.sample_rate
                )
                / (
                    (long double)source->loop.length_frames
                    * (long double)engine_sample_rate
                )
            );
            if (required_cycles > (long double)UINT64_MAX) {
                return COSMOS_MOBILE_PLAYBACK_FAILED;
            }
            completed_cycles = (ma_uint64)required_cycles;
            if (completed_cycles == 0) {
                completed_cycles = 1;
            }
            if (
                !pitched_frame_duration(
                    source->loop.length_frames,
                    completed_cycles,
                    source->loop.sample_rate,
                    engine_sample_rate,
                    source->pitch,
                    &completed_loop_frames
                )
                || !add_frames(
                    source->loop.start_frame,
                    completed_loop_frames,
                    &transition_frame
                )
            ) {
                return COSMOS_MOBILE_PLAYBACK_FAILED;
            }
            if (transition_frame < earliest_transition_frame) {
                if (
                    completed_cycles == UINT64_MAX
                    || !pitched_frame_duration(
                        source->loop.length_frames,
                        completed_cycles + 1,
                        source->loop.sample_rate,
                        engine_sample_rate,
                        source->pitch,
                        &completed_loop_frames
                    )
                    || !add_frames(
                        source->loop.start_frame,
                        completed_loop_frames,
                        &transition_frame
                    )
                ) {
                    return COSMOS_MOBILE_PLAYBACK_FAILED;
                }
            }
        }
    }
    if (source->intro.initialized) {
        ma_sound_set_stop_time_in_pcm_frames(&source->intro.sound, transition_frame);
    }
    ma_sound_set_looping(&source->loop.sound, MA_FALSE);
    ma_sound_set_stop_time_in_pcm_frames(&source->loop.sound, transition_frame);
    result = segment_schedule(&source->outro, transition_frame, MA_FALSE);
    if (result != COSMOS_MOBILE_SUCCESS) {
        return result;
    }
    source->looping = MA_FALSE;
    source->outro_scheduled = MA_TRUE;
    source->outro_requested = MA_TRUE;
    return COSMOS_MOBILE_SUCCESS;
}

void cosmos_mobile_source_stop(cosmos_mobile_source* source) {
    ma_uint32 sequence_index;
    if (source == NULL || source->stopped) {
        return;
    }
    if (source->intro.initialized) {
        ma_sound_stop(&source->intro.sound);
    }
    if (source->loop.initialized) {
        ma_sound_stop(&source->loop.sound);
    }
    if (source->outro.initialized) {
        ma_sound_stop(&source->outro.sound);
    }
    for (sequence_index = 0; sequence_index < source->sequence_count; sequence_index += 1) {
        ma_sound_stop(&source->sequence[sequence_index].sound);
    }
    if (source->group_initialized) {
        ma_sound_group_stop(&source->group);
    }
    source->stopped = MA_TRUE;
}

int32_t cosmos_mobile_source_at_end(cosmos_mobile_source* source) {
    ma_bool32 segments_ended;
    ma_uint64 now;
    ma_uint32 sequence_index;

    if (source == NULL || source->stopped) {
        return 1;
    }
    if (!source->started || source->paused || source->looping) {
        return 0;
    }
    if (source->sequence_count > 0) {
        segments_ended = MA_TRUE;
        for (
            sequence_index = 0;
            sequence_index < source->sequence_count;
            sequence_index += 1
        ) {
            if (!ma_sound_at_end(&source->sequence[sequence_index].sound)) {
                segments_ended = MA_FALSE;
                break;
            }
        }
    } else if (source->outro_scheduled) {
        segments_ended = ma_sound_at_end(&source->outro.sound);
    } else {
        segments_ended = ma_sound_at_end(&source->loop.sound);
    }
    if (!segments_ended) {
        source->end_observation_deadline = 0;
        return 0;
    }
    now = ma_engine_get_time_in_pcm_frames(source->owner->engine);
    if (source->end_observation_deadline == 0) {
        ma_phonon_binaural_node_begin_tail_drain(source->binaural_node);
        if (!add_frames(
            now,
            source->owner->hrtf_frame_size,
            &source->end_observation_deadline
        )) {
            return ma_phonon_binaural_node_tail_remaining(
                source->binaural_node
            ) ? 0 : 1;
        }
        return 0;
    }
    if (now < source->end_observation_deadline) {
        return 0;
    }
    return ma_phonon_binaural_node_tail_remaining(source->binaural_node) ? 0 : 1;
}

uint32_t cosmos_mobile_source_sequence_count(const cosmos_mobile_source* source) {
    return source != NULL ? source->sequence_count : 0;
}

uint64_t cosmos_mobile_source_sequence_duration_frames(
    const cosmos_mobile_source* source,
    uint32_t index
) {
    ma_uint64 duration = 0;
    ma_uint32 engine_sample_rate;
    const cosmos_mobile_segment* segment;
    if (
        source == NULL
        || source->owner == NULL
        || index >= source->sequence_count
    ) {
        return 0;
    }
    segment = &source->sequence[index];
    engine_sample_rate = ma_engine_get_sample_rate(source->owner->engine);
    return pitched_frame_duration(
        segment->length_frames,
        1,
        segment->sample_rate,
        engine_sample_rate,
        source->pitch,
        &duration
    ) ? duration : 0;
}
