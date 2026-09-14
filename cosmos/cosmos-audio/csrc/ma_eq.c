/*
 * ma_eq.c — 3-band biquad EQ for miniaudio.
 *
 * Coefficient derivations follow Robert Bristow-Johnson's "Cookbook formulae
 * for audio EQ biquad filter coefficients" (RBJ, 2006). Direct form I is used
 * for simplicity; numeric precision is fine at 32-bit float for typical EQ
 * settings.
 */

#include "ma_eq.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

#ifndef MA_PI
#define MA_PI 3.14159265358979323846f
#endif

/* --- Biquad primitives ---------------------------------------------- */

typedef struct {
    /* Normalized coefficients (a0 == 1). */
    float b0, b1, b2, a1, a2;
} biquad_coeffs;

typedef struct {
    float x1, x2;  /* Input history */
    float y1, y2;  /* Output history */
} biquad_state;

static inline float biquad_process(const biquad_coeffs *c, biquad_state *s, float x) {
    float y = c->b0 * x + c->b1 * s->x1 + c->b2 * s->x2 - c->a1 * s->y1 - c->a2 * s->y2;
    s->x2 = s->x1; s->x1 = x;
    s->y2 = s->y1; s->y1 = y;
    return y;
}

/* RBJ low shelf. */
static void coeffs_lowshelf(biquad_coeffs *c, float fs, float f0, float gain_db) {
    float A = powf(10.0f, gain_db / 40.0f);
    float w0 = 2.0f * MA_PI * f0 / fs;
    float cw = cosf(w0);
    float sw = sinf(w0);
    float S = 1.0f;  /* Shelf slope */
    float alpha = sw / 2.0f * sqrtf((A + 1.0f / A) * (1.0f / S - 1.0f) + 2.0f);
    float two_sqrtA_alpha = 2.0f * sqrtf(A) * alpha;

    float b0 =      A * ((A + 1.0f) - (A - 1.0f) * cw + two_sqrtA_alpha);
    float b1 = 2.0f * A * ((A - 1.0f) - (A + 1.0f) * cw);
    float b2 =      A * ((A + 1.0f) - (A - 1.0f) * cw - two_sqrtA_alpha);
    float a0 =           (A + 1.0f) + (A - 1.0f) * cw + two_sqrtA_alpha;
    float a1 =   -2.0f * ((A - 1.0f) + (A + 1.0f) * cw);
    float a2 =           (A + 1.0f) + (A - 1.0f) * cw - two_sqrtA_alpha;

    c->b0 = b0 / a0; c->b1 = b1 / a0; c->b2 = b2 / a0;
    c->a1 = a1 / a0; c->a2 = a2 / a0;
}

/* RBJ high shelf. */
static void coeffs_highshelf(biquad_coeffs *c, float fs, float f0, float gain_db) {
    float A = powf(10.0f, gain_db / 40.0f);
    float w0 = 2.0f * MA_PI * f0 / fs;
    float cw = cosf(w0);
    float sw = sinf(w0);
    float S = 1.0f;
    float alpha = sw / 2.0f * sqrtf((A + 1.0f / A) * (1.0f / S - 1.0f) + 2.0f);
    float two_sqrtA_alpha = 2.0f * sqrtf(A) * alpha;

    float b0 =       A * ((A + 1.0f) + (A - 1.0f) * cw + two_sqrtA_alpha);
    float b1 = -2.0f * A * ((A - 1.0f) + (A + 1.0f) * cw);
    float b2 =       A * ((A + 1.0f) + (A - 1.0f) * cw - two_sqrtA_alpha);
    float a0 =           (A + 1.0f) - (A - 1.0f) * cw + two_sqrtA_alpha;
    float a1 =    2.0f * ((A - 1.0f) - (A + 1.0f) * cw);
    float a2 =           (A + 1.0f) - (A - 1.0f) * cw - two_sqrtA_alpha;

    c->b0 = b0 / a0; c->b1 = b1 / a0; c->b2 = b2 / a0;
    c->a1 = a1 / a0; c->a2 = a2 / a0;
}

/* RBJ peaking EQ. */
static void coeffs_peaking(biquad_coeffs *c, float fs, float f0, float gain_db, float Q) {
    float A = powf(10.0f, gain_db / 40.0f);
    float w0 = 2.0f * MA_PI * f0 / fs;
    float cw = cosf(w0);
    float sw = sinf(w0);
    float alpha = sw / (2.0f * Q);

    float b0 = 1.0f + alpha * A;
    float b1 = -2.0f * cw;
    float b2 = 1.0f - alpha * A;
    float a0 = 1.0f + alpha / A;
    float a1 = -2.0f * cw;
    float a2 = 1.0f - alpha / A;

    c->b0 = b0 / a0; c->b1 = b1 / a0; c->b2 = b2 / a0;
    c->a1 = a1 / a0; c->a2 = a2 / a0;
}

/* --- Node struct ---------------------------------------------------- */

struct ma_eq_node {
    ma_node_base base;

    float sample_rate;

    float low_freq,  low_gain;
    float mid_freq,  mid_gain, mid_q;
    float high_freq, high_gain;

    biquad_coeffs low_c, mid_c, high_c;
    biquad_state  low_sL, low_sR;
    biquad_state  mid_sL, mid_sR;
    biquad_state  high_sL, high_sR;

    int dirty;
};

static void eq_recompute(ma_eq_node *n) {
    coeffs_lowshelf (&n->low_c,  n->sample_rate, n->low_freq,  n->low_gain);
    coeffs_peaking  (&n->mid_c,  n->sample_rate, n->mid_freq,  n->mid_gain, n->mid_q);
    coeffs_highshelf(&n->high_c, n->sample_rate, n->high_freq, n->high_gain);
    n->dirty = 0;
}

/* --- Audio process callback ----------------------------------------- */

static void eq_process_pcm_frames(
    ma_node *pNodeArg,
    const float **ppFramesIn,
    ma_uint32 *pFrameCountIn,
    float **ppFramesOut,
    ma_uint32 *pFrameCountOut)
{
    ma_eq_node *n = (ma_eq_node *)pNodeArg;
    const float *in  = ppFramesIn[0];
    float       *out = ppFramesOut[0];
    ma_uint32 frameCount = (*pFrameCountIn < *pFrameCountOut) ? *pFrameCountIn : *pFrameCountOut;

    if (n->dirty) eq_recompute(n);

    for (ma_uint32 i = 0; i < frameCount; ++i) {
        float L = in[i * 2 + 0];
        float R = in[i * 2 + 1];

        L = biquad_process(&n->low_c,  &n->low_sL,  L);
        L = biquad_process(&n->mid_c,  &n->mid_sL,  L);
        L = biquad_process(&n->high_c, &n->high_sL, L);

        R = biquad_process(&n->low_c,  &n->low_sR,  R);
        R = biquad_process(&n->mid_c,  &n->mid_sR,  R);
        R = biquad_process(&n->high_c, &n->high_sR, R);

        out[i * 2 + 0] = L;
        out[i * 2 + 1] = R;
    }

    *pFrameCountIn  = frameCount;
    *pFrameCountOut = frameCount;
}

static ma_node_vtable eq_vtable = {
    eq_process_pcm_frames,
    NULL,
    1, 1,
    0
};

/* --- Public API ----------------------------------------------------- */

MA_API ma_eq_node_config ma_eq_node_config_init(ma_uint32 channels, ma_uint32 sampleRate) {
    ma_eq_node_config cfg = {0};
    cfg.channels = (channels == 0) ? 2 : channels;
    cfg.sampleRate = sampleRate;
    cfg.nodeConfig = ma_node_config_init();
    cfg.nodeConfig.vtable = &eq_vtable;
    static const ma_uint32 in_ch[1]  = {2};
    static const ma_uint32 out_ch[1] = {2};
    cfg.nodeConfig.pInputChannels  = in_ch;
    cfg.nodeConfig.pOutputChannels = out_ch;
    return cfg;
}

MA_API ma_eq_node *ma_eq_node_alloc(void) {
    ma_eq_node *p = (ma_eq_node *)ma_malloc(sizeof(ma_eq_node), NULL);
    if (p) memset(p, 0, sizeof(*p));
    return p;
}

MA_API void ma_eq_node_free(ma_eq_node *pNode) {
    if (pNode) ma_free(pNode, NULL);
}

MA_API ma_result ma_eq_node_init(
    ma_node_graph *pGraph,
    const ma_eq_node_config *pConfig,
    const ma_allocation_callbacks *pAllocCallbacks,
    ma_eq_node *pNode)
{
    if (pNode == NULL || pGraph == NULL || pConfig == NULL) return MA_INVALID_ARGS;
    if (pConfig->channels != 2) return MA_INVALID_ARGS;

    memset(pNode, 0, sizeof(*pNode));

    ma_result r = ma_node_init(pGraph, &pConfig->nodeConfig, pAllocCallbacks, &pNode->base);
    if (r != MA_SUCCESS) return r;

    pNode->sample_rate = (pConfig->sampleRate > 0) ? (float)pConfig->sampleRate : 44100.0f;

    pNode->low_freq  = 200.0f;
    pNode->mid_freq  = 2000.0f;
    pNode->high_freq = 5000.0f;
    pNode->low_gain  = 0.0f;
    pNode->mid_gain  = 0.0f;
    pNode->high_gain = 0.0f;
    pNode->mid_q     = 1.0f;
    pNode->dirty = 1;
    eq_recompute(pNode);
    return MA_SUCCESS;
}

MA_API void ma_eq_node_uninit(ma_eq_node *pNode, const ma_allocation_callbacks *pAllocCallbacks) {
    if (pNode == NULL) return;
    ma_node_uninit(&pNode->base, pAllocCallbacks);
}

static float clampf(float x, float lo, float hi) { return x < lo ? lo : (x > hi ? hi : x); }

MA_API void ma_eq_node_set_low_gain (ma_eq_node *p, float db) { if (p) { p->low_gain  = clampf(db, -24.0f, 24.0f); p->dirty = 1; } }
MA_API void ma_eq_node_set_mid_gain (ma_eq_node *p, float db) { if (p) { p->mid_gain  = clampf(db, -24.0f, 24.0f); p->dirty = 1; } }
MA_API void ma_eq_node_set_high_gain(ma_eq_node *p, float db) { if (p) { p->high_gain = clampf(db, -24.0f, 24.0f); p->dirty = 1; } }
MA_API void ma_eq_node_set_low_freq (ma_eq_node *p, float hz) { if (p) { p->low_freq  = clampf(hz, 20.0f,  400.0f);  p->dirty = 1; } }
MA_API void ma_eq_node_set_mid_freq (ma_eq_node *p, float hz) { if (p) { p->mid_freq  = clampf(hz, 200.0f, 8000.0f); p->dirty = 1; } }
MA_API void ma_eq_node_set_high_freq(ma_eq_node *p, float hz) { if (p) { p->high_freq = clampf(hz, 2000.0f, 16000.0f); p->dirty = 1; } }
MA_API void ma_eq_node_set_mid_q    (ma_eq_node *p, float q)  { if (p) { p->mid_q     = clampf(q,  0.1f,  8.0f);    p->dirty = 1; } }
