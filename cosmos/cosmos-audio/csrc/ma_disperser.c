/*
 * ma_disperser.c — cascaded second-order allpass disperser.
 *
 * Each allpass biquad has unity magnitude at all frequencies but rotates
 * phase around its center frequency. Cascading N of them at the same
 * center gives a frequency-selective group-delay hump — transients that
 * hit that band get stretched out into a descending chirp. The classic
 * "laser gun" / "pitch drop on kicks" effect.
 */

#include "ma_disperser.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

#ifndef MA_PI
#define MA_PI 3.14159265358979323846f
#endif

/* RBJ second-order allpass: unity magnitude everywhere. */
typedef struct {
    float b0, b1, b2, a1, a2;
} ap_coeffs;

typedef struct {
    float x1, x2, y1, y2;
} ap_state;

static inline float ap_process(const ap_coeffs *c, ap_state *s, float x) {
    float y = c->b0 * x + c->b1 * s->x1 + c->b2 * s->x2 - c->a1 * s->y1 - c->a2 * s->y2;
    s->x2 = s->x1; s->x1 = x;
    s->y2 = s->y1; s->y1 = y;
    return y;
}

static void allpass_coeffs(ap_coeffs *c, float fs, float f0, float Q) {
    float w0 = 2.0f * MA_PI * f0 / fs;
    float cw = cosf(w0);
    float sw = sinf(w0);
    float alpha = sw / (2.0f * Q);

    float b0 = 1.0f - alpha;
    float b1 = -2.0f * cw;
    float b2 = 1.0f + alpha;
    float a0 = 1.0f + alpha;
    float a1 = -2.0f * cw;
    float a2 = 1.0f - alpha;

    c->b0 = b0 / a0;
    c->b1 = b1 / a0;
    c->b2 = b2 / a0;
    c->a1 = a1 / a0;
    c->a2 = a2 / a0;
}

/* --- Node struct ---------------------------------------------------- */

struct ma_disperser_node {
    ma_node_base base;

    float sample_rate;
    float freq;
    float q;
    int   stages;  /* 1..MA_DISPERSER_MAX_STAGES */

    ap_coeffs coeffs;
    ap_state  sL[MA_DISPERSER_MAX_STAGES];
    ap_state  sR[MA_DISPERSER_MAX_STAGES];

    int dirty;
};

static void disp_recompute(ma_disperser_node *n) {
    allpass_coeffs(&n->coeffs, n->sample_rate, n->freq, n->q);
    n->dirty = 0;
}

/* --- Audio process callback ----------------------------------------- */

static void disp_process_pcm_frames(
    ma_node *pNodeArg,
    const float **ppFramesIn,
    ma_uint32 *pFrameCountIn,
    float **ppFramesOut,
    ma_uint32 *pFrameCountOut)
{
    ma_disperser_node *n = (ma_disperser_node *)pNodeArg;
    const float *in  = ppFramesIn[0];
    float       *out = ppFramesOut[0];
    ma_uint32 frameCount = (*pFrameCountIn < *pFrameCountOut) ? *pFrameCountIn : *pFrameCountOut;

    if (n->dirty) disp_recompute(n);

    const int stages = n->stages;
    for (ma_uint32 i = 0; i < frameCount; ++i) {
        float L = in[i * 2 + 0];
        float R = in[i * 2 + 1];
        for (int s = 0; s < stages; ++s) {
            L = ap_process(&n->coeffs, &n->sL[s], L);
            R = ap_process(&n->coeffs, &n->sR[s], R);
        }
        out[i * 2 + 0] = L;
        out[i * 2 + 1] = R;
    }

    *pFrameCountIn  = frameCount;
    *pFrameCountOut = frameCount;
}

static ma_node_vtable disp_vtable = {
    disp_process_pcm_frames,
    NULL,
    1, 1,
    0
};

/* --- Public API ----------------------------------------------------- */

MA_API ma_disperser_node_config ma_disperser_node_config_init(ma_uint32 channels, ma_uint32 sampleRate) {
    ma_disperser_node_config cfg = {0};
    cfg.channels = (channels == 0) ? 2 : channels;
    cfg.sampleRate = sampleRate;
    cfg.nodeConfig = ma_node_config_init();
    cfg.nodeConfig.vtable = &disp_vtable;
    static const ma_uint32 in_ch[1]  = {2};
    static const ma_uint32 out_ch[1] = {2};
    cfg.nodeConfig.pInputChannels  = in_ch;
    cfg.nodeConfig.pOutputChannels = out_ch;
    return cfg;
}

MA_API ma_disperser_node *ma_disperser_node_alloc(void) {
    ma_disperser_node *p = (ma_disperser_node *)ma_malloc(sizeof(ma_disperser_node), NULL);
    if (p) memset(p, 0, sizeof(*p));
    return p;
}

MA_API void ma_disperser_node_free(ma_disperser_node *pNode) {
    if (pNode) ma_free(pNode, NULL);
}

MA_API ma_result ma_disperser_node_init(
    ma_node_graph *pGraph,
    const ma_disperser_node_config *pConfig,
    const ma_allocation_callbacks *pAllocCallbacks,
    ma_disperser_node *pNode)
{
    if (pNode == NULL || pGraph == NULL || pConfig == NULL) return MA_INVALID_ARGS;
    if (pConfig->channels != 2) return MA_INVALID_ARGS;

    memset(pNode, 0, sizeof(*pNode));

    ma_result r = ma_node_init(pGraph, &pConfig->nodeConfig, pAllocCallbacks, &pNode->base);
    if (r != MA_SUCCESS) return r;

    pNode->sample_rate = (pConfig->sampleRate > 0) ? (float)pConfig->sampleRate : 44100.0f;
    pNode->freq   = 800.0f;
    pNode->q      = 0.707f;
    pNode->stages = 8;
    pNode->dirty  = 1;
    disp_recompute(pNode);
    return MA_SUCCESS;
}

MA_API void ma_disperser_node_uninit(ma_disperser_node *pNode, const ma_allocation_callbacks *pAllocCallbacks) {
    if (pNode == NULL) return;
    ma_node_uninit(&pNode->base, pAllocCallbacks);
}

MA_API void ma_disperser_node_set_freq(ma_disperser_node *p, float hz) {
    if (!p) return;
    if (hz < 20.0f)    hz = 20.0f;
    if (hz > 18000.0f) hz = 18000.0f;
    p->freq = hz;
    p->dirty = 1;
}

MA_API void ma_disperser_node_set_q(ma_disperser_node *p, float q) {
    if (!p) return;
    if (q < 0.1f) q = 0.1f;
    if (q > 8.0f) q = 8.0f;
    p->q = q;
    p->dirty = 1;
}

MA_API void ma_disperser_node_set_stages(ma_disperser_node *p, int stages) {
    if (!p) return;
    if (stages < 1) stages = 1;
    if (stages > MA_DISPERSER_MAX_STAGES) stages = MA_DISPERSER_MAX_STAGES;
    p->stages = stages;
    /* No dirty — coefficients don't depend on stage count. */
}
