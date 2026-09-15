// miniaudio_phonon.c - Steam Audio (Phonon) integration for miniaudio
// Based on NVGT's implementation, adapted for Cosmos

#include <string.h>
#include <stdint.h>
#include <stdlib.h>
#include <math.h>
#include "miniaudio.h"
#include "phonon.h"
#include "miniaudio_phonon.h"

// Global phonon state
static IPLAudioSettings g_phonon_audio_settings = {44100, 256};
static IPLContext g_phonon_context = NULL;
static IPLHRTF g_phonon_hrtf = NULL;
static ma_bool32 g_phonon_initialized = MA_FALSE;
static ma_uint32 g_phonon_ref_count = 0;

#define MA_PHONON_PARAMETER_SNAPSHOT_ATTEMPTS 3

_Static_assert(sizeof(float) == sizeof(uint32_t), "HRTF atomic float storage requires IEEE-754-sized floats");

static void atomic_store_float(atomic_uint_least32_t* destination, float value)
{
    uint32_t bits;
    memcpy(&bits, &value, sizeof(bits));
    atomic_store_explicit(destination, bits, memory_order_seq_cst);
}

static float atomic_load_float(const atomic_uint_least32_t* source)
{
    uint32_t bits = (uint32_t)atomic_load_explicit(source, memory_order_seq_cst);
    float value;
    memcpy(&value, &bits, sizeof(value));
    return value;
}

static ma_result ma_result_from_IPLerror(IPLerror error)
{
    switch (error)
    {
        case IPL_STATUS_SUCCESS:     return MA_SUCCESS;
        case IPL_STATUS_OUTOFMEMORY: return MA_OUT_OF_MEMORY;
        case IPL_STATUS_INITIALIZATION:
        case IPL_STATUS_FAILURE:
        default: return MA_ERROR;
    }
}

MA_API ma_result ma_phonon_init(ma_uint32 sampleRate, ma_uint32 frameSize)
{
    /* Calls are serialized by the Rust lifecycle mutex. */
    if (sampleRate == 0 || frameSize == 0) return MA_INVALID_ARGS;
    if (g_phonon_initialized) {
        if (
            g_phonon_audio_settings.samplingRate != (IPLint32)sampleRate ||
            g_phonon_audio_settings.frameSize != (IPLint32)frameSize
        ) {
            return MA_INVALID_OPERATION;
        }
        g_phonon_ref_count += 1;
        return MA_SUCCESS;
    }

    g_phonon_audio_settings.samplingRate = sampleRate;
    g_phonon_audio_settings.frameSize = frameSize;

    IPLContextSettings phonon_context_settings = {0};
    phonon_context_settings.version = STEAMAUDIO_VERSION;

    if (iplContextCreate(&phonon_context_settings, &g_phonon_context) != IPL_STATUS_SUCCESS) {
        return MA_ERROR;
    }

    IPLHRTFSettings phonon_hrtf_settings = {0};
    phonon_hrtf_settings.type = IPL_HRTFTYPE_DEFAULT;
    phonon_hrtf_settings.volume = 1.0f;

    if (iplHRTFCreate(g_phonon_context, &g_phonon_audio_settings, &phonon_hrtf_settings, &g_phonon_hrtf) != IPL_STATUS_SUCCESS) {
        iplContextRelease(&g_phonon_context);
        g_phonon_context = NULL;
        return MA_ERROR;
    }

    g_phonon_initialized = MA_TRUE;
    g_phonon_ref_count = 1;
    return MA_SUCCESS;
}

MA_API void ma_phonon_uninit(void)
{
    if (!g_phonon_initialized) return;
    if (g_phonon_ref_count > 1) {
        g_phonon_ref_count -= 1;
        return;
    }

    if (g_phonon_hrtf) {
        iplHRTFRelease(&g_phonon_hrtf);
        g_phonon_hrtf = NULL;
    }
    if (g_phonon_context) {
        iplContextRelease(&g_phonon_context);
        g_phonon_context = NULL;
    }
    g_phonon_initialized = MA_FALSE;
    g_phonon_ref_count = 0;
}

MA_API IPLContext ma_phonon_get_context(void)
{
    return g_phonon_context;
}

MA_API IPLHRTF ma_phonon_get_hrtf(void)
{
    return g_phonon_hrtf;
}

MA_API IPLAudioSettings ma_phonon_get_audio_settings(void)
{
    return g_phonon_audio_settings;
}

MA_API ma_bool32 ma_phonon_is_initialized(void)
{
    return g_phonon_initialized;
}

MA_API ma_phonon_binaural_node_config ma_phonon_binaural_node_config_init(ma_uint32 channelsIn, IPLAudioSettings iplAudioSettings, IPLContext iplContext, IPLHRTF iplHRTF)
{
    ma_phonon_binaural_node_config config;

    memset(&config, 0, sizeof(ma_phonon_binaural_node_config));
    config.nodeConfig       = ma_node_config_init();
    config.channelsIn       = channelsIn;
    config.iplAudioSettings = iplAudioSettings;
    config.iplContext       = iplContext;
    config.iplHRTF          = iplHRTF;

    return config;
}

static void ma_phonon_binaural_node_process_pcm_frames(ma_node* pNode, const float** ppFramesIn, ma_uint32* pFrameCountIn, float** ppFramesOut, ma_uint32* pFrameCountOut)
{
    ma_phonon_binaural_node* pBinauralNode = (ma_phonon_binaural_node*)pNode;
    IPLAudioBuffer inputBufferDesc;
    IPLAudioBuffer outputBufferDesc;
    IPLBinauralEffectParams effectParams;
    IPLBinauralEffectParams candidateParams;
    ma_uint32 totalFramesToProcess = *pFrameCountOut;
    ma_uint32 totalFramesProcessed = 0;
    ma_uint32 paramsVersionBefore;
    ma_uint32 paramsVersionAfter;
    ma_uint32 snapshotAttempt;

    inputBufferDesc.numChannels = (IPLint32)ma_node_get_input_channels(pNode, 0);

    /* We'll run this in a loop just in case our deinterleaved buffers are too small. */
    outputBufferDesc.numSamples  = pBinauralNode->iplAudioSettings.frameSize;
    outputBufferDesc.numChannels = 2;
    outputBufferDesc.data        = pBinauralNode->ppBuffersOut;

    /*
    Read a coherent parameter snapshot without taking a lock on the audio
    thread. A control update marks the version odd while publishing fields and
    even when complete. Attempts are deliberately bounded: if the control
    thread is preempted mid-update, the callback reuses its last good snapshot
    instead of spinning and risking an audible deadline miss.
    */
    effectParams = pBinauralNode->audioThreadParams;
    for (snapshotAttempt = 0; snapshotAttempt < MA_PHONON_PARAMETER_SNAPSHOT_ATTEMPTS; snapshotAttempt += 1) {
        paramsVersionBefore = (ma_uint32)atomic_load_explicit(&pBinauralNode->paramsVersion, memory_order_seq_cst);
        if ((paramsVersionBefore & 1) != 0) {
            continue;
        }
        candidateParams = effectParams;
        candidateParams.direction.x = atomic_load_float(&pBinauralNode->directionXBits);
        candidateParams.direction.y = atomic_load_float(&pBinauralNode->directionYBits);
        candidateParams.direction.z = atomic_load_float(&pBinauralNode->directionZBits);
        candidateParams.spatialBlend = atomic_load_float(&pBinauralNode->spatialBlendBits);
        candidateParams.interpolation = (IPLHRTFInterpolation)atomic_load_explicit(&pBinauralNode->interpolation, memory_order_seq_cst);
        candidateParams.hrtf = pBinauralNode->iplHRTF;
        paramsVersionAfter = (ma_uint32)atomic_load_explicit(&pBinauralNode->paramsVersion, memory_order_seq_cst);
        if (paramsVersionBefore == paramsVersionAfter && (paramsVersionAfter & 1) == 0) {
            effectParams = candidateParams;
            pBinauralNode->audioThreadParams = candidateParams;
            break;
        }
    }

    while (totalFramesProcessed < totalFramesToProcess) {
        ma_uint32 framesToProcessThisIteration = totalFramesToProcess - totalFramesProcessed;
        if (framesToProcessThisIteration > (ma_uint32)pBinauralNode->iplAudioSettings.frameSize) {
            framesToProcessThisIteration = (ma_uint32)pBinauralNode->iplAudioSettings.frameSize;
        }

        if (inputBufferDesc.numChannels == 1) {
            memcpy(
                pBinauralNode->ppBuffersIn[0],
                ma_offset_pcm_frames_const_ptr_f32(ppFramesIn[0], totalFramesProcessed, 1),
                sizeof(float) * framesToProcessThisIteration
            );
        } else {
            ma_deinterleave_pcm_frames(ma_format_f32, inputBufferDesc.numChannels, framesToProcessThisIteration, ma_offset_pcm_frames_const_ptr_f32(ppFramesIn[0], totalFramesProcessed, inputBufferDesc.numChannels), (void**)&pBinauralNode->ppBuffersIn[0]);
        }

        /* Steam Audio effects consume the configured frame size. miniaudio's
        normal graph period matches it; zero-padding also makes a short final
        callback safe during device shutdown or graph detachment. */
        if (framesToProcessThisIteration < (ma_uint32)pBinauralNode->iplAudioSettings.frameSize) {
            ma_uint32 iChannelIn;
            for (iChannelIn = 0; iChannelIn < (ma_uint32)inputBufferDesc.numChannels; iChannelIn += 1) {
                memset(
                    pBinauralNode->ppBuffersIn[iChannelIn] + framesToProcessThisIteration,
                    0,
                    sizeof(float) * ((ma_uint32)pBinauralNode->iplAudioSettings.frameSize - framesToProcessThisIteration)
                );
            }
        }

        inputBufferDesc.data       = pBinauralNode->ppBuffersIn;
        inputBufferDesc.numSamples = pBinauralNode->iplAudioSettings.frameSize;

        /* Apply the effect. */
        iplBinauralEffectApply(pBinauralNode->iplEffect, &effectParams, &inputBufferDesc, &outputBufferDesc);

        /* Interleave straight into the output buffer. */
        ma_interleave_pcm_frames(ma_format_f32, 2, framesToProcessThisIteration, (const void**)&pBinauralNode->ppBuffersOut[0], ma_offset_pcm_frames_ptr_f32(ppFramesOut[0], totalFramesProcessed, 2));

        /* Advance. */
        totalFramesProcessed += framesToProcessThisIteration;
    }

    (void)pFrameCountIn;    /* Unused. */
}

static ma_node_vtable g_ma_phonon_binaural_node_vtable =
{
    ma_phonon_binaural_node_process_pcm_frames,
    NULL,
    1,  /* 1 input channel. */
    1,  /* 1 output channel. */
    0
};

#define ma_offset_ptr64(p, offset) ((void*)((ma_uint8*)(p) + (uintptr_t)(offset)))

MA_API ma_result ma_phonon_binaural_node_init(ma_node_graph* pNodeGraph, const ma_phonon_binaural_node_config* pConfig, const ma_allocation_callbacks* pAllocationCallbacks, ma_phonon_binaural_node* pBinauralNode)
{
    ma_result result;
    ma_node_config baseConfig;
    ma_uint32 channelsIn;
    ma_uint32 channelsOut;
    IPLBinauralEffectSettings iplBinauralEffectSettings;
    size_t heapSizeInBytes;

    if (pBinauralNode == NULL) {
        return MA_INVALID_ARGS;
    }

    memset(pBinauralNode, 0, sizeof(ma_phonon_binaural_node));

    if (pConfig == NULL || pConfig->iplAudioSettings.frameSize == 0 || pConfig->iplContext == NULL || pConfig->iplHRTF == NULL) {
        return MA_INVALID_ARGS;
    }

    /* Steam Audio only supports mono and stereo input. */
    if (pConfig->channelsIn < 1 || pConfig->channelsIn > 2) {
        return MA_INVALID_ARGS;
    }

    channelsIn  = pConfig->channelsIn;
    channelsOut = 2;    /* Always stereo output. */

    baseConfig = ma_node_config_init();
    baseConfig.vtable          = &g_ma_phonon_binaural_node_vtable;
    baseConfig.pInputChannels  = &channelsIn;
    baseConfig.pOutputChannels = &channelsOut;
    result = ma_node_init(pNodeGraph, &baseConfig, pAllocationCallbacks, &pBinauralNode->baseNode);
    if (result != MA_SUCCESS) {
        return result;
    }

    pBinauralNode->iplAudioSettings = pConfig->iplAudioSettings;
    pBinauralNode->iplContext       = pConfig->iplContext;
    pBinauralNode->iplHRTF          = pConfig->iplHRTF;

    atomic_init(&pBinauralNode->paramsVersion, 0);
    atomic_init(&pBinauralNode->directionXBits, 0);
    atomic_init(&pBinauralNode->directionYBits, 0);
    atomic_init(&pBinauralNode->directionZBits, 0);
    atomic_init(&pBinauralNode->spatialBlendBits, 0);
    atomic_init(&pBinauralNode->interpolation, (ma_uint32)IPL_HRTFINTERPOLATION_BILINEAR);
    if (!atomic_is_lock_free(&pBinauralNode->paramsVersion)) {
        ma_node_uninit(&pBinauralNode->baseNode, pAllocationCallbacks);
        return MA_NOT_IMPLEMENTED;
    }
    atomic_store_float(&pBinauralNode->directionXBits, 0.0f);
    atomic_store_float(&pBinauralNode->directionYBits, 0.0f);
    atomic_store_float(&pBinauralNode->directionZBits, -1.0f);
    atomic_store_float(&pBinauralNode->spatialBlendBits, 1.0f);
    memset(&pBinauralNode->audioThreadParams, 0, sizeof(IPLBinauralEffectParams));
    pBinauralNode->audioThreadParams.direction.z = -1.0f;
    pBinauralNode->audioThreadParams.interpolation = IPL_HRTFINTERPOLATION_BILINEAR;
    pBinauralNode->audioThreadParams.spatialBlend = 1.0f;
    pBinauralNode->audioThreadParams.hrtf = pConfig->iplHRTF;

    memset(&iplBinauralEffectSettings, 0, sizeof(IPLBinauralEffectSettings));
    iplBinauralEffectSettings.hrtf = pConfig->iplHRTF;

    result = ma_result_from_IPLerror(iplBinauralEffectCreate(pBinauralNode->iplContext, &pBinauralNode->iplAudioSettings, &iplBinauralEffectSettings, &pBinauralNode->iplEffect));
    if (result != MA_SUCCESS) {
        ma_node_uninit(&pBinauralNode->baseNode, pAllocationCallbacks);
        return result;
    }

    heapSizeInBytes = 0;

    /*
    Unfortunately Steam Audio uses deinterleaved buffers for everything so we'll need to use some
    intermediary buffers. We'll allocate one big buffer on the heap and then use offsets. We'll
    use the frame size from the IPLAudioSettings structure as a basis for the size of the buffer.
    */
    heapSizeInBytes += sizeof(float) * channelsOut * pBinauralNode->iplAudioSettings.frameSize; /* Output buffer. */
    heapSizeInBytes += sizeof(float) * channelsIn  * pBinauralNode->iplAudioSettings.frameSize; /* Input buffer. */

    pBinauralNode->_pHeap = ma_malloc(heapSizeInBytes, pAllocationCallbacks);
    if (pBinauralNode->_pHeap == NULL) {
        iplBinauralEffectRelease(&pBinauralNode->iplEffect);
        ma_node_uninit(&pBinauralNode->baseNode, pAllocationCallbacks);
        return MA_OUT_OF_MEMORY;
    }

    pBinauralNode->ppBuffersOut[0] = (float*)pBinauralNode->_pHeap;
    pBinauralNode->ppBuffersOut[1] = (float*)ma_offset_ptr64(pBinauralNode->_pHeap, sizeof(float) * pBinauralNode->iplAudioSettings.frameSize);

    {
        ma_uint32 iChannelIn;
        for (iChannelIn = 0; iChannelIn < channelsIn; iChannelIn += 1) {
            pBinauralNode->ppBuffersIn[iChannelIn] = (float*)ma_offset_ptr64(pBinauralNode->_pHeap, sizeof(float) * pBinauralNode->iplAudioSettings.frameSize * (channelsOut + iChannelIn));
        }
    }

    return MA_SUCCESS;
}

MA_API void ma_phonon_binaural_node_uninit(ma_phonon_binaural_node* pBinauralNode, const ma_allocation_callbacks* pAllocationCallbacks)
{
    if (pBinauralNode == NULL) {
        return;
    }
    /* The base node is always uninitialized first. */
    ma_node_uninit(&pBinauralNode->baseNode, pAllocationCallbacks);
    /*
    The Steam Audio objects are deleted after the base node. This ensures the base node is removed from the graph
    first to ensure these objects aren't getting used by the audio thread.
    */
    iplBinauralEffectRelease(&pBinauralNode->iplEffect);
    ma_free(pBinauralNode->_pHeap, pAllocationCallbacks);
}

MA_API ma_result ma_phonon_binaural_node_set_parameters(ma_phonon_binaural_node* pBinauralNode, float x, float y, float z, float spatialBlend, IPLHRTFInterpolation interpolation)
{
    ma_uint32 version;
    if (
        pBinauralNode == NULL ||
        !isfinite(x) || !isfinite(y) || !isfinite(z) || !isfinite(spatialBlend) ||
        spatialBlend < 0.0f || spatialBlend > 1.0f ||
        (interpolation != IPL_HRTFINTERPOLATION_NEAREST && interpolation != IPL_HRTFINTERPOLATION_BILINEAR)
    ) {
        return MA_INVALID_ARGS;
    }

    version = (ma_uint32)atomic_load_explicit(&pBinauralNode->paramsVersion, memory_order_seq_cst);
    if ((version & 1) != 0) {
        version += 1;
    }
    atomic_store_explicit(&pBinauralNode->paramsVersion, version + 1, memory_order_seq_cst);
    atomic_store_float(&pBinauralNode->directionXBits, x);
    atomic_store_float(&pBinauralNode->directionYBits, y);
    atomic_store_float(&pBinauralNode->directionZBits, z);
    atomic_store_float(&pBinauralNode->spatialBlendBits, spatialBlend);
    atomic_store_explicit(&pBinauralNode->interpolation, (ma_uint32)interpolation, memory_order_seq_cst);
    atomic_store_explicit(&pBinauralNode->paramsVersion, version + 2, memory_order_seq_cst);
    return MA_SUCCESS;
}

// Allocation functions for D bindings (ensures correct struct sizes)
MA_API ma_phonon_binaural_node* ma_phonon_binaural_node_alloc(void)
{
    return (ma_phonon_binaural_node*)malloc(sizeof(ma_phonon_binaural_node));
}

MA_API void ma_phonon_binaural_node_free(ma_phonon_binaural_node* pNode)
{
    free(pNode);
}
