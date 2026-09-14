/*
 * ma_distortion.c — tanh waveshaper / overdrive for miniaudio.
 *
 * Per sample: y = tanh(drive * x) / tanh(drive)   (normalized so unity input
 * stays near unity), then a one-pole low-pass "tone" stage, then wet/dry mix.
 */

#include "ma_distortion.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

#ifndef MA_PI
#define MA_PI 3.14159265358979323846f
#endif

static float clampf(float x, float lo, float hi) { return x < lo ? lo : (x > hi ? hi : x); }

struct ma_distortion_node {
    ma_node_base base;
    float sample_rate;

    float drive;
    float tone;     /* Hz */
    float wet;
    float dry;

    float norm;     /* 1 / tanh(drive), cached. */
    float tone_a;   /* One-pole coefficient, cached. */
    float lpL, lpR; /* One-pole LP state. */
    int dirty;
};

static void dist_recompute(ma_distortion_node *n) {
    float t = tanhf(n->drive);
    n->norm = (t > 0.0001f) ? (1.0f / t) : 1.0f;
    float fc = n->tone / n->sample_rate;
    if (fc > 0.49f) fc = 0.49f;
    n->tone_a = 1.0f - expf(-2.0f * MA_PI * fc);
    n->dirty = 0;
}

/* --- Audio process callback ----------------------------------------- */

static void dist_process_pcm_frames(
    ma_node *pNodeArg,
    const float **ppFramesIn,
    ma_uint32 *pFrameCountIn,
    float **ppFramesOut,
    ma_uint32 *pFrameCountOut)
{
    ma_distortion_node *n = (ma_distortion_node *)pNodeArg;
    const float *in  = ppFramesIn[0];
    float       *out = ppFramesOut[0];
    ma_uint32 frameCount = (*pFrameCountIn < *pFrameCountOut) ? *pFrameCountIn : *pFrameCountOut;

    if (n->dirty) dist_recompute(n);

    for (ma_uint32 i = 0; i < frameCount; ++i) {
        float dryL = in[i * 2 + 0];
        float dryR = in[i * 2 + 1];

        float shapedL = tanhf(n->drive * dryL) * n->norm;
        float shapedR = tanhf(n->drive * dryR) * n->norm;

        /* One-pole low-pass tone stage. */
        n->lpL += n->tone_a * (shapedL - n->lpL);
        n->lpR += n->tone_a * (shapedR - n->lpR);

        out[i * 2 + 0] = dryL * n->dry + n->lpL * n->wet;
        out[i * 2 + 1] = dryR * n->dry + n->lpR * n->wet;
    }

    *pFrameCountIn  = frameCount;
    *pFrameCountOut = frameCount;
}

static ma_node_vtable dist_vtable = {
    dist_process_pcm_frames,
    NULL,
    1, 1,
    0
};

/* --- Public API ----------------------------------------------------- */

MA_API ma_distortion_node_config ma_distortion_node_config_init(ma_uint32 channels, ma_uint32 sampleRate) {
    ma_distortion_node_config cfg = {0};
    cfg.channels = (channels == 0) ? 2 : channels;
    cfg.sampleRate = sampleRate;
    cfg.nodeConfig = ma_node_config_init();
    cfg.nodeConfig.vtable = &dist_vtable;
    static const ma_uint32 in_ch[1]  = {2};
    static const ma_uint32 out_ch[1] = {2};
    cfg.nodeConfig.pInputChannels  = in_ch;
    cfg.nodeConfig.pOutputChannels = out_ch;
    return cfg;
}

MA_API ma_distortion_node *ma_distortion_node_alloc(void) {
    ma_distortion_node *p = (ma_distortion_node *)ma_malloc(sizeof(ma_distortion_node), NULL);
    if (p) memset(p, 0, sizeof(*p));
    return p;
}

MA_API void ma_distortion_node_free(ma_distortion_node *pNode) {
    if (pNode) ma_free(pNode, NULL);
}

MA_API ma_result ma_distortion_node_init(
    ma_node_graph *pGraph,
    const ma_distortion_node_config *pConfig,
    const ma_allocation_callbacks *pAllocCallbacks,
    ma_distortion_node *pNode)
{
    if (pNode == NULL || pGraph == NULL || pConfig == NULL) return MA_INVALID_ARGS;
    if (pConfig->channels != 2) return MA_INVALID_ARGS;

    memset(pNode, 0, sizeof(*pNode));

    ma_result r = ma_node_init(pGraph, &pConfig->nodeConfig, pAllocCallbacks, &pNode->base);
    if (r != MA_SUCCESS) return r;

    pNode->sample_rate = (pConfig->sampleRate > 0) ? (float)pConfig->sampleRate : 44100.0f;
    pNode->drive = 4.0f;
    pNode->tone  = 8000.0f;
    pNode->wet   = 0.5f;
    pNode->dry   = 0.5f;
    pNode->lpL = pNode->lpR = 0.0f;
    pNode->dirty = 1;
    dist_recompute(pNode);
    return MA_SUCCESS;
}

MA_API void ma_distortion_node_uninit(ma_distortion_node *pNode, const ma_allocation_callbacks *pAllocCallbacks) {
    if (pNode == NULL) return;
    ma_node_uninit(&pNode->base, pAllocCallbacks);
}

MA_API void ma_distortion_node_set_drive(ma_distortion_node *p, float drive) { if (p) { p->drive = clampf(drive, 1.0f, 50.0f);     p->dirty = 1; } }
MA_API void ma_distortion_node_set_tone (ma_distortion_node *p, float hz)    { if (p) { p->tone  = clampf(hz, 200.0f, 18000.0f);   p->dirty = 1; } }
MA_API void ma_distortion_node_set_wet  (ma_distortion_node *p, float wet)   { if (p) { p->wet   = clampf(wet, 0.0f, 1.0f); } }
MA_API void ma_distortion_node_set_dry  (ma_distortion_node *p, float dry)   { if (p) { p->dry   = clampf(dry, 0.0f, 1.0f); } }
