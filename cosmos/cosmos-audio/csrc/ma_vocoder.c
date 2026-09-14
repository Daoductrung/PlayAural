/*
 * ma_vocoder.c — advanced single-input channel vocoder for miniaudio.
 *
 * Modulator (input, summed to mono) → bank of N RBJ bandpass filters →
 * per-band envelope follower. Carrier (internal saw/pulse/noise/supersaw, with
 * optional pitch randomization and stereo detune) → a parallel band bank whose
 * centers are formant-shifted → each band scaled by the modulator envelope →
 * summed, soft-clipped, plus optional unvoiced-high passthrough (sibilance).
 * Output = dry*input + wet*vocoded.
 */

#include "ma_vocoder.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

#ifndef MA_PI
#define MA_PI 3.14159265358979323846f
#endif

#define MA_VOCODER_MAX_BANDS 32
#define MA_VOCODER_FMIN 120.0f
#define MA_VOCODER_FMAX 7000.0f
#define MA_VOCODER_SIB_HZ 3500.0f

static float clampf(float x, float lo, float hi) { return x < lo ? lo : (x > hi ? hi : x); }

typedef struct { float b0, b1, b2, a1, a2; } biquad_coeffs;
typedef struct { float x1, x2, y1, y2; } biquad_state;

static inline float biquad_process(const biquad_coeffs *c, biquad_state *s, float x) {
    float y = c->b0 * x + c->b1 * s->x1 + c->b2 * s->x2 - c->a1 * s->y1 - c->a2 * s->y2;
    s->x2 = s->x1; s->x1 = x;
    s->y2 = s->y1; s->y1 = y;
    return y;
}

/* RBJ bandpass (constant 0 dB peak gain). */
static void coeffs_bandpass(biquad_coeffs *c, float fs, float f0, float Q) {
    float w0 = 2.0f * MA_PI * (f0 / fs);
    float cw = cosf(w0), sw = sinf(w0);
    if (Q < 0.0001f) Q = 0.0001f;
    float alpha = sw / (2.0f * Q);
    float b0 = alpha, b1 = 0.0f, b2 = -alpha;
    float a0 = 1.0f + alpha, a1 = -2.0f * cw, a2 = 1.0f - alpha;
    c->b0 = b0 / a0; c->b1 = b1 / a0; c->b2 = b2 / a0;
    c->a1 = a1 / a0; c->a2 = a2 / a0;
}

/* Supersaw voice detune ratios. */
static const float SUPERSAW_DETUNE[3] = { 0.9940f, 1.0000f, 1.0060f };

struct ma_vocoder_node {
    ma_node_base base;
    float sample_rate;

    int   bands;
    int   carrier;
    float carrier_freq;
    float attack_ms;
    float release_ms;
    float wet;
    float dry;

    /* Advanced */
    int   rand_on;
    float rand_rate;     /* Hz */
    float rand_depth;    /* octaves */
    float formant;       /* carrier band scale */
    float spread;        /* stereo detune 0..1 */
    float sibilance;     /* unvoiced HP passthrough 0..1 */

    /* Band banks — separate coeffs so the carrier can be formant-shifted. */
    biquad_coeffs mod_c[MA_VOCODER_MAX_BANDS];
    biquad_coeffs car_c[MA_VOCODER_MAX_BANDS];
    biquad_state  mod_s[MA_VOCODER_MAX_BANDS];
    biquad_state  car_sL[MA_VOCODER_MAX_BANDS];
    biquad_state  car_sR[MA_VOCODER_MAX_BANDS];
    float         env[MA_VOCODER_MAX_BANDS];

    float atk_coeff, rel_coeff;

    /* Carrier oscillators (3 voices per channel for supersaw). */
    float phaseL[3], phaseR[3];
    unsigned int rng;

    /* Randomization. */
    float rand_freq;     /* Current chosen pitch. */
    float rand_timer;    /* Samples until next pick. */

    /* Sibilance highpass state (one-pole). */
    float sib_r, hp_x1, hp_y1;

    int dirty;
};

static inline float noise_next(ma_vocoder_node *n) {
    n->rng = n->rng * 1664525u + 1013904223u;
    return ((float)(n->rng >> 9) / 8388608.0f) - 1.0f;  /* [-1, 1) */
}

static void vocoder_recompute(ma_vocoder_node *n) {
    int N = n->bands;
    if (N < 1) N = 1;
    if (N > MA_VOCODER_MAX_BANDS) N = MA_VOCODER_MAX_BANDS;

    float ratio = powf(MA_VOCODER_FMAX / MA_VOCODER_FMIN, 1.0f / (float)((N > 1) ? (N - 1) : 1));
    float Q = (ratio > 1.0001f) ? (sqrtf(ratio) / (ratio - 1.0f)) : 4.0f;
    Q = clampf(Q, 1.0f, 20.0f);
    float nyq = n->sample_rate * 0.45f;

    for (int b = 0; b < N; ++b) {
        float f0 = MA_VOCODER_FMIN * powf(ratio, (float)b);
        float fm = clampf(f0, 20.0f, nyq);
        float fc = clampf(f0 * n->formant, 20.0f, nyq);
        coeffs_bandpass(&n->mod_c[b], n->sample_rate, fm, Q);
        coeffs_bandpass(&n->car_c[b], n->sample_rate, fc, Q);
    }

    float atk = n->attack_ms  * 0.001f * n->sample_rate;
    float rel = n->release_ms * 0.001f * n->sample_rate;
    n->atk_coeff = (atk > 1.0f) ? (1.0f - expf(-1.0f / atk)) : 1.0f;
    n->rel_coeff = (rel > 1.0f) ? (1.0f - expf(-1.0f / rel)) : 1.0f;

    n->sib_r = expf(-2.0f * MA_PI * MA_VOCODER_SIB_HZ / n->sample_rate);
    n->dirty = 0;
}

/* One carrier sample for a channel, advancing its phase voices. */
static inline float carrier_gen(ma_vocoder_node *n, float *phases, float freq) {
    switch (n->carrier) {
        case MA_VOCODER_CARRIER_NOISE:
            return noise_next(n);
        case MA_VOCODER_CARRIER_PULSE: {
            float out = (phases[0] < 0.5f) ? 1.0f : -1.0f;
            phases[0] += freq / n->sample_rate;
            if (phases[0] >= 1.0f) phases[0] -= 1.0f;
            return out;
        }
        case MA_VOCODER_CARRIER_SUPERSAW: {
            float out = 0.0f;
            for (int v = 0; v < 3; ++v) {
                out += 2.0f * phases[v] - 1.0f;
                phases[v] += (freq * SUPERSAW_DETUNE[v]) / n->sample_rate;
                if (phases[v] >= 1.0f) phases[v] -= 1.0f;
            }
            return out * (1.0f / 3.0f);
        }
        case MA_VOCODER_CARRIER_SAW:
        default: {
            float out = 2.0f * phases[0] - 1.0f;
            phases[0] += freq / n->sample_rate;
            if (phases[0] >= 1.0f) phases[0] -= 1.0f;
            return out;
        }
    }
}

static void vocoder_process_pcm_frames(
    ma_node *pNodeArg,
    const float **ppFramesIn,
    ma_uint32 *pFrameCountIn,
    float **ppFramesOut,
    ma_uint32 *pFrameCountOut)
{
    ma_vocoder_node *n = (ma_vocoder_node *)pNodeArg;
    const float *in  = ppFramesIn[0];
    float       *out = ppFramesOut[0];
    ma_uint32 frameCount = (*pFrameCountIn < *pFrameCountOut) ? *pFrameCountIn : *pFrameCountOut;

    if (n->dirty) vocoder_recompute(n);

    int N = n->bands;
    if (N < 1) N = 1;
    if (N > MA_VOCODER_MAX_BANDS) N = MA_VOCODER_MAX_BANDS;

    float makeup = 2.0f + 0.25f * (float)N;
    float rand_period = n->sample_rate / clampf(n->rand_rate, 0.1f, 30.0f);
    if (rand_period < 1.0f) rand_period = 1.0f;
    float spread_amt = n->spread * 0.02f;  /* up to ±2% detune */

    for (ma_uint32 i = 0; i < frameCount; ++i) {
        float dryL = in[i * 2 + 0];
        float dryR = in[i * 2 + 1];
        float mod  = (dryL + dryR) * 0.5f;

        float base = n->carrier_freq;
        if (n->rand_on) {
            n->rand_timer -= 1.0f;
            if (n->rand_timer <= 0.0f) {
                float u = noise_next(n);  /* [-1,1] */
                n->rand_freq = n->carrier_freq * powf(2.0f, u * n->rand_depth);
                n->rand_freq = clampf(n->rand_freq, 20.0f, 2000.0f);
                n->rand_timer = rand_period;
            }
            base = n->rand_freq;
        }

        float genL = carrier_gen(n, n->phaseL, base * (1.0f - spread_amt));
        float genR = carrier_gen(n, n->phaseR, base * (1.0f + spread_amt));

        float accL = 0.0f, accR = 0.0f;
        for (int b = 0; b < N; ++b) {
            float m = biquad_process(&n->mod_c[b], &n->mod_s[b], mod);
            float a = fabsf(m);
            float coeff = (a > n->env[b]) ? n->atk_coeff : n->rel_coeff;
            n->env[b] += coeff * (a - n->env[b]);

            accL += biquad_process(&n->car_c[b], &n->car_sL[b], genL) * n->env[b];
            accR += biquad_process(&n->car_c[b], &n->car_sR[b], genR) * n->env[b];
        }

        float wetL = tanhf(accL * makeup);
        float wetR = tanhf(accR * makeup);

        if (n->sibilance > 0.0f) {
            /* One-pole highpass of the modulator → unvoiced consonants. */
            float hp = n->sib_r * (n->hp_y1 + mod - n->hp_x1);
            n->hp_x1 = mod;
            n->hp_y1 = hp;
            wetL += hp * n->sibilance;
            wetR += hp * n->sibilance;
        }

        out[i * 2 + 0] = dryL * n->dry + wetL * n->wet;
        out[i * 2 + 1] = dryR * n->dry + wetR * n->wet;
    }

    *pFrameCountIn  = frameCount;
    *pFrameCountOut = frameCount;
}

static ma_node_vtable vocoder_vtable = {
    vocoder_process_pcm_frames,
    NULL,
    1, 1,
    0
};

MA_API ma_vocoder_node_config ma_vocoder_node_config_init(ma_uint32 channels, ma_uint32 sampleRate) {
    ma_vocoder_node_config cfg = {0};
    cfg.channels = (channels == 0) ? 2 : channels;
    cfg.sampleRate = sampleRate;
    cfg.nodeConfig = ma_node_config_init();
    cfg.nodeConfig.vtable = &vocoder_vtable;
    static const ma_uint32 in_ch[1]  = {2};
    static const ma_uint32 out_ch[1] = {2};
    cfg.nodeConfig.pInputChannels  = in_ch;
    cfg.nodeConfig.pOutputChannels = out_ch;
    return cfg;
}

MA_API ma_vocoder_node *ma_vocoder_node_alloc(void) {
    ma_vocoder_node *p = (ma_vocoder_node *)ma_malloc(sizeof(ma_vocoder_node), NULL);
    if (p) memset(p, 0, sizeof(*p));
    return p;
}

MA_API void ma_vocoder_node_free(ma_vocoder_node *pNode) {
    if (pNode) ma_free(pNode, NULL);
}

MA_API ma_result ma_vocoder_node_init(
    ma_node_graph *pGraph,
    const ma_vocoder_node_config *pConfig,
    const ma_allocation_callbacks *pAllocCallbacks,
    ma_vocoder_node *pNode)
{
    if (pNode == NULL || pGraph == NULL || pConfig == NULL) return MA_INVALID_ARGS;
    if (pConfig->channels != 2) return MA_INVALID_ARGS;

    memset(pNode, 0, sizeof(*pNode));

    ma_result r = ma_node_init(pGraph, &pConfig->nodeConfig, pAllocCallbacks, &pNode->base);
    if (r != MA_SUCCESS) return r;

    pNode->sample_rate = (pConfig->sampleRate > 0) ? (float)pConfig->sampleRate : 44100.0f;
    pNode->bands = 16;
    pNode->carrier = MA_VOCODER_CARRIER_SAW;
    pNode->carrier_freq = 110.0f;
    pNode->attack_ms = 5.0f;
    pNode->release_ms = 60.0f;
    pNode->wet = 1.0f;
    pNode->dry = 0.0f;

    pNode->rand_on = 0;
    pNode->rand_rate = 6.0f;
    pNode->rand_depth = 1.0f;
    pNode->formant = 1.0f;
    pNode->spread = 0.0f;
    pNode->sibilance = 0.0f;

    pNode->rng = 22222u;
    pNode->rand_freq = pNode->carrier_freq;
    pNode->rand_timer = 0.0f;
    pNode->dirty = 1;
    vocoder_recompute(pNode);
    return MA_SUCCESS;
}

MA_API void ma_vocoder_node_uninit(ma_vocoder_node *pNode, const ma_allocation_callbacks *pAllocCallbacks) {
    if (pNode == NULL) return;
    ma_node_uninit(&pNode->base, pAllocCallbacks);
}

MA_API void ma_vocoder_node_set_bands(ma_vocoder_node *p, int bands) {
    if (!p) return;
    if (bands < 4) bands = 4;
    if (bands > MA_VOCODER_MAX_BANDS) bands = MA_VOCODER_MAX_BANDS;
    p->bands = bands;
    p->dirty = 1;
}
MA_API void ma_vocoder_node_set_carrier(ma_vocoder_node *p, int carrier) {
    if (!p) return;
    if (carrier < 0) carrier = 0;
    if (carrier > MA_VOCODER_CARRIER_SUPERSAW) carrier = MA_VOCODER_CARRIER_SUPERSAW;
    p->carrier = carrier;
}
MA_API void ma_vocoder_node_set_carrier_freq(ma_vocoder_node *p, float hz) { if (p) p->carrier_freq = clampf(hz, 40.0f, 800.0f); }
MA_API void ma_vocoder_node_set_attack (ma_vocoder_node *p, float ms) { if (p) { p->attack_ms  = clampf(ms, 0.1f, 100.0f); p->dirty = 1; } }
MA_API void ma_vocoder_node_set_release(ma_vocoder_node *p, float ms) { if (p) { p->release_ms = clampf(ms, 1.0f, 500.0f); p->dirty = 1; } }
MA_API void ma_vocoder_node_set_wet    (ma_vocoder_node *p, float wet){ if (p) p->wet = clampf(wet, 0.0f, 1.0f); }
MA_API void ma_vocoder_node_set_dry    (ma_vocoder_node *p, float dry){ if (p) p->dry = clampf(dry, 0.0f, 1.0f); }

MA_API void ma_vocoder_node_set_rand      (ma_vocoder_node *p, int on)       { if (p) p->rand_on = on ? 1 : 0; }
MA_API void ma_vocoder_node_set_rand_rate (ma_vocoder_node *p, float hz)     { if (p) p->rand_rate = clampf(hz, 0.1f, 30.0f); }
MA_API void ma_vocoder_node_set_rand_depth(ma_vocoder_node *p, float oct)    { if (p) p->rand_depth = clampf(oct, 0.0f, 4.0f); }
MA_API void ma_vocoder_node_set_formant   (ma_vocoder_node *p, float factor) { if (p) { p->formant = clampf(factor, 0.25f, 4.0f); p->dirty = 1; } }
MA_API void ma_vocoder_node_set_spread    (ma_vocoder_node *p, float spread) { if (p) p->spread = clampf(spread, 0.0f, 1.0f); }
MA_API void ma_vocoder_node_set_sibilance (ma_vocoder_node *p, float amt)    { if (p) p->sibilance = clampf(amt, 0.0f, 1.0f); }
