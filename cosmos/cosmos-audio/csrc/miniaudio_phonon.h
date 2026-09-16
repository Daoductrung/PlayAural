// miniaudio_phonon.h - Steam Audio (Phonon) integration for miniaudio
// Based on NVGT's implementation

#pragma once

#include <stdatomic.h>
#include "phonon.h"
#include "miniaudio.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct
{
    ma_node_config nodeConfig;
    ma_uint32 channelsIn;
    IPLAudioSettings iplAudioSettings;
    IPLContext iplContext;
    IPLHRTF iplHRTF;   /* There is one HRTF object to many binaural effect objects. */
} ma_phonon_binaural_node_config;

MA_API ma_phonon_binaural_node_config ma_phonon_binaural_node_config_init(ma_uint32 channelsIn, IPLAudioSettings iplAudioSettings, IPLContext iplContext, IPLHRTF iplHRTF);


typedef struct
{
    ma_node_base baseNode;
    IPLAudioSettings iplAudioSettings;
    IPLContext iplContext;
    IPLBinauralEffect iplEffect;
    IPLHRTF iplHRTF;

    /*
    Control-thread parameters are read by miniaudio's real-time callback.
    Every scalar is accessed with C11 atomics and paramsVersion
    provides a lock-free, coherent snapshot of the complete parameter set.
    */
    atomic_uint_least32_t paramsVersion;
    atomic_uint_least32_t directionXBits;
    atomic_uint_least32_t directionYBits;
    atomic_uint_least32_t directionZBits;
    atomic_uint_least32_t spatialBlendBits;
    atomic_uint_least32_t interpolation;
    atomic_uint_least32_t tailRemaining;

    /* Last coherent snapshot, owned exclusively by the audio callback. */
    IPLBinauralEffectParams audioThreadParams;

    /* Fixed-frame adapter state used by continuous mobile rendering. */
    ma_uint32 bufferedInputFrames;
    ma_uint32 bufferedOutputFrames;
    ma_uint32 bufferedOutputOffset;
    IPLAudioEffectState bufferedEffectState;

    float* ppBuffersIn[2];      /* Each buffer is an offset of _pHeap. */
    float* ppBuffersOut[2];     /* Each buffer is an offset of _pHeap. */
    void* _pHeap;
} ma_phonon_binaural_node;

MA_API ma_result ma_phonon_binaural_node_init(ma_node_graph* pNodeGraph, const ma_phonon_binaural_node_config* pConfig, const ma_allocation_callbacks* pAllocationCallbacks, ma_phonon_binaural_node* pBinauralNode);
MA_API ma_result ma_phonon_binaural_node_init_with_tail_processing(ma_node_graph* pNodeGraph, const ma_phonon_binaural_node_config* pConfig, const ma_allocation_callbacks* pAllocationCallbacks, ma_phonon_binaural_node* pBinauralNode);
MA_API void ma_phonon_binaural_node_uninit(ma_phonon_binaural_node* pBinauralNode, const ma_allocation_callbacks* pAllocationCallbacks);
MA_API ma_result ma_phonon_binaural_node_set_parameters(ma_phonon_binaural_node* pBinauralNode, float x, float y, float z, float spatialBlend, IPLHRTFInterpolation interpolation);
MA_API ma_bool32 ma_phonon_binaural_node_tail_remaining(const ma_phonon_binaural_node* pBinauralNode);
MA_API ma_phonon_binaural_node* ma_phonon_binaural_node_alloc(void);
MA_API void ma_phonon_binaural_node_free(ma_phonon_binaural_node* pNode);

// Global phonon context management
MA_API ma_result ma_phonon_init(ma_uint32 sampleRate, ma_uint32 frameSize);
MA_API void ma_phonon_uninit(void);
MA_API IPLContext ma_phonon_get_context(void);
MA_API IPLHRTF ma_phonon_get_hrtf(void);
MA_API IPLAudioSettings ma_phonon_get_audio_settings(void);
MA_API ma_bool32 ma_phonon_is_initialized(void);

#ifdef __cplusplus
}
#endif
