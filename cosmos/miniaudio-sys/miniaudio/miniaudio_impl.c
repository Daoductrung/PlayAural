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

#include <stdlib.h>

typedef struct {
    ma_engine engine;
    ma_resource_manager resourceManager;
    ma_bool32 resourceManagerInitialized;
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

    return MA_SUCCESS;
}

void ma_engine_uninit_with_caching(ma_engine* pEngine) {
    cosmos_engine* pCosmosEngine;
    if (pEngine == NULL) {
        return;
    }
    pCosmosEngine = (cosmos_engine*)pEngine;
    ma_engine_uninit(pEngine);

    if (pCosmosEngine->resourceManagerInitialized) {
        ma_resource_manager_uninit(&pCosmosEngine->resourceManager);
        pCosmosEngine->resourceManagerInitialized = MA_FALSE;
    }
}

// Node graph functions for HRTF integration
ma_node* ma_sound_get_node_ptr(ma_sound* pSound) {
    return &pSound->engineNode.baseNode;
}
