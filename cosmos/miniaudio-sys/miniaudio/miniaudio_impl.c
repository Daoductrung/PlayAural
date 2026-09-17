// Miniaudio implementation file
// This is compiled by build.rs

// Include stb_vorbis for OGG support
#define STB_VORBIS_HEADER_ONLY
#include "stb_vorbis.c"

#define MINIAUDIO_IMPLEMENTATION
#include "miniaudio.h"

// Now include the stb_vorbis implementation
#undef STB_VORBIS_HEADER_ONLY
#include "stb_vorbis.c"

#include <stdint.h>
#include <stdlib.h>

typedef struct {
    ma_engine engine;
    ma_resource_manager resourceManager;
    ma_context context;
    ma_device device;
    ma_bool32 resourceManagerInitialized;
    ma_bool32 contextInitialized;
    ma_bool32 deviceInitialized;
    ma_bool32 engineInitialized;
} cosmos_engine;

// Helper functions for Rust bindings - allocate opaque structs. The resource
// manager belongs to its engine; this permits multiple independent Cosmos
// managers without sharing or prematurely freeing a process-global cache.
ma_engine* ma_engine_alloc(void) {
    cosmos_engine* engine = (cosmos_engine*)calloc(1, sizeof(cosmos_engine));
    return engine != NULL ? &engine->engine : NULL;
}

void ma_engine_free(ma_engine* engine) {
    free((cosmos_engine*)engine);
}

ma_sound* ma_sound_alloc(void) {
    return (ma_sound*)malloc(sizeof(ma_sound));
}

void ma_sound_free(ma_sound* sound) {
    free(sound);
}

static void cosmos_engine_data_callback(
    ma_device* pDevice,
    void* pFramesOut,
    const void* pFramesIn,
    ma_uint32 frameCount
) {
    ma_engine* pEngine = (ma_engine*)pDevice->pUserData;
    (void)pFramesIn;
    if (ma_engine_read_pcm_frames(pEngine, pFramesOut, frameCount, NULL) != MA_SUCCESS) {
        ma_silence_pcm_frames(
            pFramesOut,
            frameCount,
            pDevice->playback.format,
            pDevice->playback.channels
        );
    }
}

ma_result ma_engine_init_with_caching(ma_engine* pEngine, ma_uint32 periodSizeInFrames) {
    ma_result result;
    cosmos_engine* pCosmosEngine;

    if (pEngine == NULL || periodSizeInFrames == 0) {
        return MA_INVALID_ARGS;
    }
    pCosmosEngine = (cosmos_engine*)pEngine;

    // Create resource manager for caching decoded audio
    ma_resource_manager_config rmConfig = ma_resource_manager_config_init();
    result = ma_resource_manager_init(&rmConfig, &pCosmosEngine->resourceManager);
    if (result != MA_SUCCESS) {
        return result;
    }
    pCosmosEngine->resourceManagerInitialized = MA_TRUE;

    // Create engine with resource manager
    ma_engine_config engineConfig = ma_engine_config_init();
    engineConfig.pResourceManager = &pCosmosEngine->resourceManager;
    engineConfig.periodSizeInFrames = periodSizeInFrames;

    result = ma_engine_init(&engineConfig, pEngine);
    if (result != MA_SUCCESS) {
        ma_resource_manager_uninit(&pCosmosEngine->resourceManager);
        pCosmosEngine->resourceManagerInitialized = MA_FALSE;
        return result;
    }
    pCosmosEngine->engineInitialized = MA_TRUE;

    return MA_SUCCESS;
}

/*
The mobile engine owns its context and playback device so it can declare media
usage without asking miniaudio to select an output or mutate the application's
audio-session category. Expo AV remains the single audio-focus/session owner.
*/
ma_result ma_engine_init_mobile_with_caching(
    ma_engine* pEngine,
    ma_uint32 periodSizeInFrames,
    ma_uint32 parameterSmoothingMilliseconds
) {
    ma_result result;
    cosmos_engine* pCosmosEngine;
    ma_resource_manager_config resourceManagerConfig;
    ma_context_config contextConfig;
    ma_device_config deviceConfig;
    ma_engine_config engineConfig;
    ma_uint64 parameterSmoothingFrames;

    if (pEngine == NULL || periodSizeInFrames == 0) {
        return MA_INVALID_ARGS;
    }
    pCosmosEngine = (cosmos_engine*)pEngine;

    contextConfig = ma_context_config_init();
#if defined(__APPLE__)
    contextConfig.coreaudio.sessionCategory = ma_ios_session_category_none;
    contextConfig.coreaudio.noAudioSessionActivate = MA_TRUE;
    contextConfig.coreaudio.noAudioSessionDeactivate = MA_TRUE;
#endif
    result = ma_context_init(NULL, 0, &contextConfig, &pCosmosEngine->context);
    if (result != MA_SUCCESS) {
        goto on_error;
    }
    pCosmosEngine->contextInitialized = MA_TRUE;

    deviceConfig = ma_device_config_init(ma_device_type_playback);
    deviceConfig.playback.pDeviceID = NULL;
    deviceConfig.playback.format = ma_format_f32;
    deviceConfig.playback.channels = 2;
    deviceConfig.periodSizeInFrames = periodSizeInFrames;
    deviceConfig.dataCallback = cosmos_engine_data_callback;
    deviceConfig.pUserData = pEngine;
#if defined(__ANDROID__)
    deviceConfig.opensl.streamType = ma_opensl_stream_type_media;
    deviceConfig.aaudio.usage = ma_aaudio_usage_media;
    deviceConfig.aaudio.contentType = ma_aaudio_content_type_music;
#endif
    result = ma_device_init(&pCosmosEngine->context, &deviceConfig, &pCosmosEngine->device);
    if (result != MA_SUCCESS) {
        goto on_error;
    }
    pCosmosEngine->deviceInitialized = MA_TRUE;

    /* Decode into the graph's actual format and sample rate. Besides avoiding
    redundant per-source conversion, this makes PCM-frame lengths suitable for
    sample-accurate intro/loop/outro scheduling. */
    resourceManagerConfig = ma_resource_manager_config_init();
    resourceManagerConfig.decodedFormat = ma_format_f32;
    resourceManagerConfig.decodedChannels = 0;
    resourceManagerConfig.decodedSampleRate = pCosmosEngine->device.sampleRate;
    result = ma_resource_manager_init(
        &resourceManagerConfig,
        &pCosmosEngine->resourceManager
    );
    if (result != MA_SUCCESS) {
        goto on_error;
    }
    pCosmosEngine->resourceManagerInitialized = MA_TRUE;

    engineConfig = ma_engine_config_init();
    engineConfig.pResourceManager = &pCosmosEngine->resourceManager;
    engineConfig.pContext = &pCosmosEngine->context;
    engineConfig.pDevice = &pCosmosEngine->device;
    engineConfig.periodSizeInFrames = periodSizeInFrames;
    parameterSmoothingFrames = (
        (ma_uint64)pCosmosEngine->device.sampleRate
        * parameterSmoothingMilliseconds
    ) / 1000;
    if (parameterSmoothingFrames > UINT32_MAX) {
        result = MA_INVALID_ARGS;
        goto on_error;
    }
    engineConfig.defaultVolumeSmoothTimeInPCMFrames = (ma_uint32)parameterSmoothingFrames;
    result = ma_engine_init(&engineConfig, pEngine);
    if (result != MA_SUCCESS) {
        goto on_error;
    }
    pCosmosEngine->engineInitialized = MA_TRUE;
    return MA_SUCCESS;

on_error:
    if (pCosmosEngine->deviceInitialized) {
        ma_device_uninit(&pCosmosEngine->device);
        pCosmosEngine->deviceInitialized = MA_FALSE;
    }
    if (pCosmosEngine->resourceManagerInitialized) {
        ma_resource_manager_uninit(&pCosmosEngine->resourceManager);
        pCosmosEngine->resourceManagerInitialized = MA_FALSE;
    }
    if (pCosmosEngine->contextInitialized) {
        ma_context_uninit(&pCosmosEngine->context);
        pCosmosEngine->contextInitialized = MA_FALSE;
    }
    return result;
}

void ma_engine_uninit_with_caching(ma_engine* pEngine) {
    cosmos_engine* pCosmosEngine;
    if (pEngine == NULL) {
        return;
    }
    pCosmosEngine = (cosmos_engine*)pEngine;
    if (pCosmosEngine->engineInitialized) {
        ma_engine_uninit(pEngine);
        pCosmosEngine->engineInitialized = MA_FALSE;
    }

    if (pCosmosEngine->deviceInitialized) {
        ma_device_uninit(&pCosmosEngine->device);
        pCosmosEngine->deviceInitialized = MA_FALSE;
    }

    /* The externally owned device must be retired before its callback's
     * resource manager. This follows miniaudio's advanced-engine teardown
     * contract and prevents a late callback from reading released decode
     * state. */
    if (pCosmosEngine->resourceManagerInitialized) {
        ma_resource_manager_uninit(&pCosmosEngine->resourceManager);
        pCosmosEngine->resourceManagerInitialized = MA_FALSE;
    }

    if (pCosmosEngine->contextInitialized) {
        ma_context_uninit(&pCosmosEngine->context);
        pCosmosEngine->contextInitialized = MA_FALSE;
    }
}

// Node graph functions for HRTF integration
ma_node* ma_sound_get_node_ptr(ma_sound* pSound) {
    return &pSound->engineNode.baseNode;
}
