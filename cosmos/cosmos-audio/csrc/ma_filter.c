/*
 * ma_filter.c — multimode biquad filter for miniaudio.
 *
 * Single RBJ biquad per channel, mode-switchable. Coefficient derivations
 * follow Robert Bristow-Johnson's "Cookbook formulae for audio EQ biquad
 * filter coefficients" (RBJ, 2006). Direct form I.
 */

#include "ma_filter.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

#ifndef MA_PI
#define MA_PI 3.14159265358979323846f
#endif

/* --- Biquad primitives ---------------------------------------------- */

typedef struct {
    float b0, b1, b2, a1, a2;  /* Normalized (a0 == 1). */
} biquad_coeffs;

typedef struct {
    float x1, x2, y1, y2;
} biquad_state;

static inline float biquad_process(const biquad_coeffs *c, biquad_state *s, float x) {
    float y = c->b0 * x + c->b1 * s->x1 + c->b2 * s->x2 - c->a1 * s->y1 - c->a2 * s->y2;
    s->x2 = s->x1; s->x1 = x;
    s->y2 = s->y1; s->y1 = y;
    return y;
}

static float clampf(float x, float lo, float hi) { return x < lo ? lo : (x > hi ? hi : x); }

/* Compute biquad coefficients for the given mode. */
static void compute_coeffs(biquad_coeffs *c, int mode, float fs, float f0, float Q, float gain_db) {
    float w0 = 2.0f * MA_PI * (f0 / fs);
    float cw = cosf(w0);
    float sw = sinf(w0);
    if (Q < 0.0001f) Q = 0.0001f;
    float alpha = sw / (2.0f * Q);
    float b0, b1, b2, a0, a1, a2;

    switch (mode) {
        case MA_FILTER_HIGHPASS:
            b0 =  (1.0f + cw) / 2.0f;
            b1 = -(1.0f + cw);
            b2 =  (1.0f + cw) / 2.0f;
            a0 =   1.0f + alpha;
            a1 =  -2.0f * cw;
            a2 =   1.0f - alpha;
            break;
        case MA_FILTER_BANDPASS:  /* constant 0 dB peak gain */
            b0 =   alpha;
            b1 =   0.0f;
            b2 =  -alpha;
            a0 =   1.0f + alpha;
            a1 =  -2.0f * cw;
            a2 =   1.0f - alpha;
            break;
        case MA_FILTER_NOTCH:
            b0 =   1.0f;
            b1 =  -2.0f * cw;
            b2 =   1.0f;
            a0 =   1.0f + alpha;
            a1 =  -2.0f * cw;
            a2 =   1.0f - alpha;
            break;
        case MA_FILTER_ALLPASS:
            b0 =   1.0f - alpha;
            b1 =  -2.0f * cw;
            b2 =   1.0f + alpha;
            a0 =   1.0f + alpha;
            a1 =  -2.0f * cw;
            a2 =   1.0f - alpha;
            break;
        case MA_FILTER_PEAK: {
            float A = powf(10.0f, gain_db / 40.0f);
            b0 =   1.0f + alpha * A;
            b1 =  -2.0f * cw;
            b2 =   1.0f - alpha * A;
            a0 =   1.0f + alpha / A;
            a1 =  -2.0f * cw;
            a2 =   1.0f - alpha / A;
            break;
        }
        case MA_FILTER_LOWSHELF: {
            float A = powf(10.0f, gain_db / 40.0f);
            float ts = 2.0f * sqrtf(A) * alpha;
            b0 =      A * ((A + 1.0f) - (A - 1.0f) * cw + ts);
            b1 = 2.0f * A * ((A - 1.0f) - (A + 1.0f) * cw);
            b2 =      A * ((A + 1.0f) - (A - 1.0f) * cw - ts);
            a0 =          (A + 1.0f) + (A - 1.0f) * cw + ts;
            a1 = -2.0f *  ((A - 1.0f) + (A + 1.0f) * cw);
            a2 =          (A + 1.0f) + (A - 1.0f) * cw - ts;
            break;
        }
        case MA_FILTER_HIGHSHELF: {
            float A = powf(10.0f, gain_db / 40.0f);
            float ts = 2.0f * sqrtf(A) * alpha;
            b0 =       A * ((A + 1.0f) + (A - 1.0f) * cw + ts);
            b1 = -2.0f * A * ((A - 1.0f) + (A + 1.0f) * cw);
            b2 =       A * ((A + 1.0f) + (A - 1.0f) * cw - ts);
            a0 =           (A + 1.0f) - (A - 1.0f) * cw + ts;
            a1 =  2.0f *   ((A - 1.0f) - (A + 1.0f) * cw);
            a2 =           (A + 1.0f) - (A - 1.0f) * cw - ts;
            break;
        }
        case MA_FILTER_LOWPASS:
        default:
            b0 =  (1.0f - cw) / 2.0f;
            b1 =   1.0f - cw;
            b2 =  (1.0f - cw) / 2.0f;
            a0 =   1.0f + alpha;
            a1 =  -2.0f * cw;
            a2 =   1.0f - alpha;
            break;
    }

    c->b0 = b0 / a0; c->b1 = b1 / a0; c->b2 = b2 / a0;
    c->a1 = a1 / a0; c->a2 = a2 / a0;
}

/* --- Node struct ---------------------------------------------------- */

struct ma_filter_node {
    ma_node_base base;
    float sample_rate;

    int   mode;
    float freq;
    float q;
    float gain;

    biquad_coeffs coeffs;
    biquad_state  sL, sR;
    int dirty;
};

static void filter_recompute(ma_filter_node *n) {
    compute_coeffs(&n->coeffs, n->mode, n->sample_rate, n->freq, n->q, n->gain);
    n->dirty = 0;
}

/* --- Audio process callback ----------------------------------------- */

static void filter_process_pcm_frames(
    ma_node *pNodeArg,
    const float **ppFramesIn,
    ma_uint32 *pFrameCountIn,
    float **ppFramesOut,
    ma_uint32 *pFrameCountOut)
{
    ma_filter_node *n = (ma_filter_node *)pNodeArg;
    const float *in  = ppFramesIn[0];
    float       *out = ppFramesOut[0];
    ma_uint32 frameCount = (*pFrameCountIn < *pFrameCountOut) ? *pFrameCountIn : *pFrameCountOut;

    if (n->dirty) filter_recompute(n);

    for (ma_uint32 i = 0; i < frameCount; ++i) {
        out[i * 2 + 0] = biquad_process(&n->coeffs, &n->sL, in[i * 2 + 0]);
        out[i * 2 + 1] = biquad_process(&n->coeffs, &n->sR, in[i * 2 + 1]);
    }

    *pFrameCountIn  = frameCount;
    *pFrameCountOut = frameCount;
}

static ma_node_vtable filter_vtable = {
    filter_process_pcm_frames,
    NULL,
    1, 1,
    0
};

/* --- Public API ----------------------------------------------------- */

MA_API ma_filter_node_config ma_filter_node_config_init(ma_uint32 channels, ma_uint32 sampleRate) {
    ma_filter_node_config cfg = {0};
    cfg.channels = (channels == 0) ? 2 : channels;
    cfg.sampleRate = sampleRate;
    cfg.nodeConfig = ma_node_config_init();
    cfg.nodeConfig.vtable = &filter_vtable;
    static const ma_uint32 in_ch[1]  = {2};
    static const ma_uint32 out_ch[1] = {2};
    cfg.nodeConfig.pInputChannels  = in_ch;
    cfg.nodeConfig.pOutputChannels = out_ch;
    return cfg;
}

MA_API ma_filter_node *ma_filter_node_alloc(void) {
    ma_filter_node *p = (ma_filter_node *)ma_malloc(sizeof(ma_filter_node), NULL);
    if (p) memset(p, 0, sizeof(*p));
    return p;
}

MA_API void ma_filter_node_free(ma_filter_node *pNode) {
    if (pNode) ma_free(pNode, NULL);
}

MA_API ma_result ma_filter_node_init(
    ma_node_graph *pGraph,
    const ma_filter_node_config *pConfig,
    const ma_allocation_callbacks *pAllocCallbacks,
    ma_filter_node *pNode)
{
    if (pNode == NULL || pGraph == NULL || pConfig == NULL) return MA_INVALID_ARGS;
    if (pConfig->channels != 2) return MA_INVALID_ARGS;

    memset(pNode, 0, sizeof(*pNode));

    ma_result r = ma_node_init(pGraph, &pConfig->nodeConfig, pAllocCallbacks, &pNode->base);
    if (r != MA_SUCCESS) return r;

    pNode->sample_rate = (pConfig->sampleRate > 0) ? (float)pConfig->sampleRate : 44100.0f;
    pNode->mode = MA_FILTER_LOWPASS;
    pNode->freq = 1000.0f;
    pNode->q    = 0.707f;
    pNode->gain = 0.0f;
    pNode->dirty = 1;
    filter_recompute(pNode);
    return MA_SUCCESS;
}

MA_API void ma_filter_node_uninit(ma_filter_node *pNode, const ma_allocation_callbacks *pAllocCallbacks) {
    if (pNode == NULL) return;
    ma_node_uninit(&pNode->base, pAllocCallbacks);
}

MA_API void ma_filter_node_set_mode(ma_filter_node *p, int mode) {
    if (!p) return;
    if (mode < 0) mode = 0;
    if (mode > MA_FILTER_ALLPASS) mode = MA_FILTER_ALLPASS;
    p->mode = mode;
    p->dirty = 1;
}
MA_API void ma_filter_node_set_freq(ma_filter_node *p, float hz) { if (p) { p->freq = clampf(hz, 20.0f, 20000.0f); p->dirty = 1; } }
MA_API void ma_filter_node_set_q   (ma_filter_node *p, float q)  { if (p) { p->q    = clampf(q,  0.1f,  24.0f);    p->dirty = 1; } }
MA_API void ma_filter_node_set_gain(ma_filter_node *p, float db) { if (p) { p->gain = clampf(db, -24.0f, 24.0f);   p->dirty = 1; } }
