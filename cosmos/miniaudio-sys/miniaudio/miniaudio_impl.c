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

// Helper functions for Rust bindings - allocate opaque structs
ma_engine* ma_engine_alloc(void) {
    return (ma_engine*)malloc(sizeof(ma_engine));
}

void ma_engine_free(ma_engine* engine) {
    free(engine);
}

ma_sound* ma_sound_alloc(void) {
    return (ma_sound*)malloc(sizeof(ma_sound));
}

void ma_sound_free(ma_sound* sound) {
    free(sound);
}

// Resource manager for sound caching
static ma_resource_manager* g_resource_manager = NULL;

ma_result ma_engine_init_with_caching(ma_engine* pEngine) {
    ma_result result;

    // Create resource manager for caching decoded audio
    g_resource_manager = (ma_resource_manager*)malloc(sizeof(ma_resource_manager));
    if (g_resource_manager == NULL) {
        return MA_OUT_OF_MEMORY;
    }

    ma_resource_manager_config rmConfig = ma_resource_manager_config_init();
    result = ma_resource_manager_init(&rmConfig, g_resource_manager);
    if (result != MA_SUCCESS) {
        free(g_resource_manager);
        g_resource_manager = NULL;
        return result;
    }

    // Create engine with resource manager
    ma_engine_config engineConfig = ma_engine_config_init();
    engineConfig.pResourceManager = g_resource_manager;
    // Fixed period size for Steam Audio compatibility (must match phonon frame size)
    engineConfig.periodSizeInFrames = 512;

    result = ma_engine_init(&engineConfig, pEngine);
    if (result != MA_SUCCESS) {
        ma_resource_manager_uninit(g_resource_manager);
        free(g_resource_manager);
        g_resource_manager = NULL;
        return result;
    }

    return MA_SUCCESS;
}

void ma_engine_uninit_with_caching(ma_engine* pEngine) {
    ma_engine_uninit(pEngine);

    if (g_resource_manager != NULL) {
        ma_resource_manager_uninit(g_resource_manager);
        free(g_resource_manager);
        g_resource_manager = NULL;
    }
}

// Node graph functions for HRTF integration
ma_node* ma_sound_get_node_ptr(ma_sound* pSound) {
    return &pSound->engineNode.baseNode;
}
