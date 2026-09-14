/*
 * ma_delay.c — stereo feedback delay / echo for miniaudio.
 *
 * Per-channel circular buffer. Read tap is `delay_samples` behind the write
 * head; feedback re-injects the delayed signal. Output = dry*input + wet*delayed.
 */

#include "ma_delay.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

#define MA_DELAY_MAX_MS 2000.0f

static float clampf(float x, float lo, float hi) { return x < lo ? lo : (x > hi ? hi : x); }

struct ma_delay_fx {
    ma_node_base base;
    float sample_rate;

    float delay_ms;
    float feedback;
    float wet;
    float dry;

    float *bufL;
    float *bufR;
    ma_uint32 cap;       /* Buffer capacity in frames. */
    ma_uint32 write;     /* Write head. */
};

/* --- Audio process callback ----------------------------------------- */

static void delay_process_pcm_frames(
    ma_node *pNodeArg,
    const float **ppFramesIn,
    ma_uint32 *pFrameCountIn,
    float **ppFramesOut,
    ma_uint32 *pFrameCountOut)
{
    ma_delay_fx *n = (ma_delay_fx *)pNodeArg;
    const float *in  = ppFramesIn[0];
    float       *out = ppFramesOut[0];
    ma_uint32 frameCount = (*pFrameCountIn < *pFrameCountOut) ? *pFrameCountIn : *pFrameCountOut;

    if (n->cap == 0 || n->bufL == NULL || n->bufR == NULL) {
        /* Pass-through if the buffer never allocated. */
        for (ma_uint32 i = 0; i < frameCount * 2; ++i) out[i] = in[i];
        *pFrameCountIn = frameCount; *pFrameCountOut = frameCount;
        return;
    }

    ma_uint32 delay_samples = (ma_uint32)(n->delay_ms * 0.001f * n->sample_rate);
    if (delay_samples < 1) delay_samples = 1;
    if (delay_samples >= n->cap) delay_samples = n->cap - 1;

    for (ma_uint32 i = 0; i < frameCount; ++i) {
        float dryL = in[i * 2 + 0];
        float dryR = in[i * 2 + 1];

        ma_uint32 read = (n->write + n->cap - delay_samples) % n->cap;
        float delL = n->bufL[read];
        float delR = n->bufR[read];

        /* Write input + feedback of the delayed signal into the line. */
        n->bufL[n->write] = dryL + delL * n->feedback;
        n->bufR[n->write] = dryR + delR * n->feedback;
        n->write = (n->write + 1) % n->cap;

        out[i * 2 + 0] = dryL * n->dry + delL * n->wet;
        out[i * 2 + 1] = dryR * n->dry + delR * n->wet;
    }

    *pFrameCountIn  = frameCount;
    *pFrameCountOut = frameCount;
}

static ma_node_vtable delay_vtable = {
    delay_process_pcm_frames,
    NULL,
    1, 1,
    0
};

/* --- Public API ----------------------------------------------------- */

MA_API ma_delay_fx_config ma_delay_fx_config_init(ma_uint32 channels, ma_uint32 sampleRate) {
    ma_delay_fx_config cfg = {0};
    cfg.channels = (channels == 0) ? 2 : channels;
    cfg.sampleRate = sampleRate;
    cfg.nodeConfig = ma_node_config_init();
    cfg.nodeConfig.vtable = &delay_vtable;
    static const ma_uint32 in_ch[1]  = {2};
    static const ma_uint32 out_ch[1] = {2};
    cfg.nodeConfig.pInputChannels  = in_ch;
    cfg.nodeConfig.pOutputChannels = out_ch;
    return cfg;
}

MA_API ma_delay_fx *ma_delay_fx_alloc(void) {
    ma_delay_fx *p = (ma_delay_fx *)ma_malloc(sizeof(ma_delay_fx), NULL);
    if (p) memset(p, 0, sizeof(*p));
    return p;
}

MA_API void ma_delay_fx_free(ma_delay_fx *pNode) {
    if (pNode) ma_free(pNode, NULL);
}

MA_API ma_result ma_delay_fx_init(
    ma_node_graph *pGraph,
    const ma_delay_fx_config *pConfig,
    const ma_allocation_callbacks *pAllocCallbacks,
    ma_delay_fx *pNode)
{
    if (pNode == NULL || pGraph == NULL || pConfig == NULL) return MA_INVALID_ARGS;
    if (pConfig->channels != 2) return MA_INVALID_ARGS;

    memset(pNode, 0, sizeof(*pNode));

    ma_result r = ma_node_init(pGraph, &pConfig->nodeConfig, pAllocCallbacks, &pNode->base);
    if (r != MA_SUCCESS) return r;

    pNode->sample_rate = (pConfig->sampleRate > 0) ? (float)pConfig->sampleRate : 44100.0f;
    pNode->delay_ms = 300.0f;
    pNode->feedback = 0.35f;
    pNode->wet = 0.35f;
    pNode->dry = 1.0f;

    pNode->cap = (ma_uint32)(MA_DELAY_MAX_MS * 0.001f * pNode->sample_rate) + 1;
    pNode->bufL = (float *)ma_malloc(sizeof(float) * pNode->cap, NULL);
    pNode->bufR = (float *)ma_malloc(sizeof(float) * pNode->cap, NULL);
    if (pNode->bufL == NULL || pNode->bufR == NULL) {
        if (pNode->bufL) ma_free(pNode->bufL, NULL);
        if (pNode->bufR) ma_free(pNode->bufR, NULL);
        pNode->bufL = pNode->bufR = NULL;
        pNode->cap = 0;
        ma_node_uninit(&pNode->base, pAllocCallbacks);
        return MA_OUT_OF_MEMORY;
    }
    memset(pNode->bufL, 0, sizeof(float) * pNode->cap);
    memset(pNode->bufR, 0, sizeof(float) * pNode->cap);
    pNode->write = 0;
    return MA_SUCCESS;
}

MA_API void ma_delay_fx_uninit(ma_delay_fx *pNode, const ma_allocation_callbacks *pAllocCallbacks) {
    if (pNode == NULL) return;
    if (pNode->bufL) { ma_free(pNode->bufL, NULL); pNode->bufL = NULL; }
    if (pNode->bufR) { ma_free(pNode->bufR, NULL); pNode->bufR = NULL; }
    pNode->cap = 0;
    ma_node_uninit(&pNode->base, pAllocCallbacks);
}

MA_API void ma_delay_fx_set_delay_ms(ma_delay_fx *p, float ms) { if (p) p->delay_ms = clampf(ms, 1.0f, MA_DELAY_MAX_MS); }
MA_API void ma_delay_fx_set_feedback(ma_delay_fx *p, float fb) { if (p) p->feedback = clampf(fb, 0.0f, 0.95f); }
MA_API void ma_delay_fx_set_wet     (ma_delay_fx *p, float wet){ if (p) p->wet = clampf(wet, 0.0f, 1.0f); }
MA_API void ma_delay_fx_set_dry     (ma_delay_fx *p, float dry){ if (p) p->dry = clampf(dry, 0.0f, 1.0f); }
