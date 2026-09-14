/*
 * ma_convreverb.c — Convolution (impulse-response) reverb node for miniaudio.
 *
 * Uniformly-partitioned overlap-save (UPOLS) FFT convolution. Stereo, true
 * channel-wise convolution (inL*irL, inR*irR). A hand-rolled radix-2 FFT does
 * the heavy lifting; impulse responses are decoded with miniaudio's decoder
 * and resampled to the engine sample rate.
 *
 * Threading: the partitioned filter lives in a double-buffered "convolver".
 * The control thread builds a fresh convolver (decode / decay reshape /
 * partition FFTs) into the inactive slot, then flips `active` — a single
 * aligned int write the audio thread latches once per process call. Live
 * scalar params (wet/dry/predelay/gain/width/cuts) need no rebuild.
 */

#include "ma_convreverb.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* --- Tuning --------------------------------------------------------- */

#define CR_BLOCK    256                 /* partition / hop size (frames)   */
#define CR_FFT      (CR_BLOCK * 2)      /* FFT size (overlap-save)         */
#define CR_RING     8192               /* dry / wet alignment ring (> max process block) */
#define CR_RING_MASK (CR_RING - 1)
#define CR_MAX_IR_SECONDS 6.0f         /* hard cap on loaded IR length     */
#define CR_PI 3.14159265358979323846f

typedef struct { float re, im; } cr_cpx;

/* --- Partitioned filter + input FDL (the swappable unit) ------------ */

typedef struct cr_convolver {
    int     K;          /* partition count = ceil(ir_frames / CR_BLOCK) */
    cr_cpx *filtL;      /* [K * CR_FFT] partition spectra, left  */
    cr_cpx *filtR;      /* [K * CR_FFT] partition spectra, right */
    cr_cpx *fdlL;       /* [K * CR_FFT] input spectrum ring, left  */
    cr_cpx *fdlR;       /* [K * CR_FFT] input spectrum ring, right */
    int     fdl_pos;    /* ring write slot [0,K) */
} cr_convolver;

/* --- Node ----------------------------------------------------------- */

struct ma_convreverb_node {
    ma_node_base base;   /* Must be first. */
    ma_uint32 sampleRate;

    /* FFT plan (size CR_FFT). */
    int    bitrev[CR_FFT];
    cr_cpx tw[CR_FFT / 2];

    /* Double-buffered convolver. The audio thread reads conv[active]. */
    cr_convolver *conv[2];
    volatile int  active;

    /* Decoded raw IR cache (engine SR, planar stereo) so decay changes can
     * rebuild without re-decoding. */
    float *rawL, *rawR;
    int    raw_frames;

    /* --- Streaming state (audio thread) --- */
    float  inAccumL[CR_BLOCK], inAccumR[CR_BLOCK]; /* current partial block (predelayed) */
    int    accumFill;
    float  prevBlockL[CR_BLOCK], prevBlockR[CR_BLOCK]; /* overlap-save history */
    cr_cpx work[CR_FFT];   /* scratch for FFT/IFFT */
    cr_cpx acc[CR_FFT];    /* scratch for spectral accumulation */

    /* Dry/wet alignment rings (absolute index, masked). */
    float dryRingL[CR_RING], dryRingR[CR_RING];
    float wetRingL[CR_RING], wetRingR[CR_RING];
    unsigned long long wpos;   /* absolute input frame counter */

    /* Pre-delay ring (feeds the convolver input only). */
    float *predL, *predR;
    int    predCap, predMask, predPos;

    /* Wet tone shaping (one-pole HP "lowcut" + one-pole LP "highcut"). */
    float hp_xL, hp_yL, hp_xR, hp_yR;  /* highpass state */
    float lp_yL, lp_yR;                /* lowpass state */
    float hp_R, lp_a;                  /* coefficients */
    volatile int filt_dirty;

    /* --- Live params (control thread writes, audio reads) --- */
    volatile float p_wet, p_dry, p_gain, p_width;
    volatile float p_predelay_ms;
    volatile float p_lowcut_hz, p_highcut_hz;
    volatile float p_diffuse;          /* 0 = wet follows source pan, 1 = mono send */
    volatile float p_decay;            /* cached; rebuild reads it */
};

/* --- Small helpers -------------------------------------------------- */

static float cr_clamp(float v, float lo, float hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

static int cr_nextpow2(int v) {
    int p = 1;
    while (p < v) p <<= 1;
    return p;
}

static unsigned int cr_rng_state = 0x1234567u;
static float cr_white(void) {
    /* xorshift32 → [-1,1) */
    cr_rng_state ^= cr_rng_state << 13;
    cr_rng_state ^= cr_rng_state >> 17;
    cr_rng_state ^= cr_rng_state << 5;
    return ((float)(cr_rng_state & 0xFFFFFF) / 8388608.0f) - 1.0f;
}

/* --- FFT ------------------------------------------------------------ */

static void cr_fft_plan(ma_convreverb_node *n) {
    int N = CR_FFT;
    /* bit reversal */
    int bits = 0;
    while ((1 << bits) < N) bits++;
    for (int i = 0; i < N; ++i) {
        int r = 0;
        for (int b = 0; b < bits; ++b)
            if (i & (1 << b)) r |= 1 << (bits - 1 - b);
        n->bitrev[i] = r;
    }
    /* forward twiddles: w_N^k = exp(-2pi i k / N) */
    for (int k = 0; k < N / 2; ++k) {
        float a = -2.0f * CR_PI * (float)k / (float)N;
        n->tw[k].re = cosf(a);
        n->tw[k].im = sinf(a);
    }
}

/* In-place radix-2 FFT. inverse!=0 conjugates twiddles and scales by 1/N. */
static void cr_fft(const ma_convreverb_node *n, cr_cpx *x, int inverse) {
    int N = CR_FFT;
    const int *br = n->bitrev;
    for (int i = 0; i < N; ++i) {
        int j = br[i];
        if (j > i) { cr_cpx t = x[i]; x[i] = x[j]; x[j] = t; }
    }
    for (int len = 2; len <= N; len <<= 1) {
        int half = len >> 1;
        int step = N / len;
        for (int i = 0; i < N; i += len) {
            int ti = 0;
            for (int j = 0; j < half; ++j) {
                cr_cpx w = n->tw[ti];
                if (inverse) w.im = -w.im;
                cr_cpx *a = &x[i + j];
                cr_cpx *b = &x[i + j + half];
                float br_ = w.re * b->re - w.im * b->im;
                float bi_ = w.re * b->im + w.im * b->re;
                float ar = a->re, ai = a->im;
                a->re = ar + br_; a->im = ai + bi_;
                b->re = ar - br_; b->im = ai - bi_;
                ti += step;
            }
        }
    }
    if (inverse) {
        float inv = 1.0f / (float)N;
        for (int i = 0; i < N; ++i) { x[i].re *= inv; x[i].im *= inv; }
    }
}

/* --- Convolver build / free ----------------------------------------- */

static void cr_convolver_free(cr_convolver *c) {
    if (!c) return;
    free(c->filtL); free(c->filtR);
    free(c->fdlL);  free(c->fdlR);
    c->filtL = c->filtR = c->fdlL = c->fdlR = NULL;
    c->K = 0;
    c->fdl_pos = 0;
}

/* Partition `frames` of planar stereo IR (irL/irR) into convolver `c`.
 * Allocates fresh buffers (caller frees any prior contents first). */
static int cr_convolver_build(ma_convreverb_node *n, cr_convolver *c,
                              const float *irL, const float *irR, int frames) {
    int K = (frames + CR_BLOCK - 1) / CR_BLOCK;
    if (K < 1) K = 1;
    size_t spec = (size_t)K * CR_FFT;
    c->filtL = (cr_cpx *)calloc(spec, sizeof(cr_cpx));
    c->filtR = (cr_cpx *)calloc(spec, sizeof(cr_cpx));
    c->fdlL  = (cr_cpx *)calloc(spec, sizeof(cr_cpx));
    c->fdlR  = (cr_cpx *)calloc(spec, sizeof(cr_cpx));
    if (!c->filtL || !c->filtR || !c->fdlL || !c->fdlR) {
        cr_convolver_free(c);
        return 0;
    }
    c->K = K;
    c->fdl_pos = 0;

    for (int k = 0; k < K; ++k) {
        cr_cpx *fl = &c->filtL[(size_t)k * CR_FFT];
        cr_cpx *fr = &c->filtR[(size_t)k * CR_FFT];
        /* First half = this IR chunk, second half = zeros (already zeroed). */
        for (int i = 0; i < CR_BLOCK; ++i) {
            int idx = k * CR_BLOCK + i;
            float sl = (idx < frames) ? irL[idx] : 0.0f;
            float sr = (idx < frames) ? irR[idx] : 0.0f;
            fl[i].re = sl; fl[i].im = 0.0f;
            fr[i].re = sr; fr[i].im = 0.0f;
        }
        cr_fft(n, fl, 0);
        cr_fft(n, fr, 0);
    }
    return 1;
}

/* Build the partitioned filter from the cached raw IR, applying the current
 * decay envelope + energy normalization, then atomically publish it. Runs on
 * the control thread. Returns 1 on success. */
static int cr_rebuild(ma_convreverb_node *n) {
    if (!n->rawL || !n->rawR || n->raw_frames <= 0) return 0;
    int frames = n->raw_frames;

    float *tmpL = (float *)malloc(sizeof(float) * (size_t)frames);
    float *tmpR = (float *)malloc(sizeof(float) * (size_t)frames);
    if (!tmpL || !tmpR) { free(tmpL); free(tmpR); return 0; }

    /* Decay reshape: env(t) = exp(-tailK * t/frames). decay=1 → flat. */
    float decay = cr_clamp(n->p_decay, 0.05f, 1.0f);
    float tailK = (1.0f / decay - 1.0f) * 6.0f;

    double energy = 0.0;
    for (int i = 0; i < frames; ++i) {
        float e = (tailK > 0.0f) ? expf(-tailK * (float)i / (float)frames) : 1.0f;
        float l = n->rawL[i] * e;
        float r = n->rawR[i] * e;
        tmpL[i] = l; tmpR[i] = r;
        energy += (double)l * l + (double)r * r;
    }
    /* Unit-energy normalize so wet level is roughly IR-independent. */
    float norm = (energy > 1e-12) ? (float)(1.0 / sqrt(energy / 2.0)) : 1.0f;
    for (int i = 0; i < frames; ++i) { tmpL[i] *= norm; tmpR[i] *= norm; }

    int inactive = n->active ^ 1;
    cr_convolver *c = n->conv[inactive];
    if (c == NULL) {
        c = (cr_convolver *)calloc(1, sizeof(cr_convolver));
        if (!c) { free(tmpL); free(tmpR); return 0; }
        n->conv[inactive] = c;
    } else {
        cr_convolver_free(c);  /* reuse the slot — safe: inactive */
    }

    int ok = cr_convolver_build(n, c, tmpL, tmpR, frames);
    free(tmpL); free(tmpR);
    if (!ok) return 0;

    n->active = inactive;  /* publish */
    return 1;
}

/* --- Block convolution (audio thread) ------------------------------- */

static void cr_process_channel(ma_convreverb_node *n, cr_convolver *c,
                               const float *prevBlock, const float *curBlock,
                               cr_cpx *filt, cr_cpx *fdl,
                               int fdl_pos_in, float *outB /* CR_BLOCK */) {
    int N = CR_FFT, K = c->K;
    cr_cpx *X = n->work;
    /* overlap-save input: [prev | cur] */
    for (int i = 0; i < CR_BLOCK; ++i) { X[i].re = prevBlock[i]; X[i].im = 0.0f; }
    for (int i = 0; i < CR_BLOCK; ++i) { X[CR_BLOCK + i].re = curBlock[i]; X[CR_BLOCK + i].im = 0.0f; }
    cr_fft(n, X, 0);

    /* store newest spectrum at slot fdl_pos_in */
    cr_cpx *slot = &fdl[(size_t)fdl_pos_in * N];
    memcpy(slot, X, sizeof(cr_cpx) * N);

    /* Y = sum_k filt[k] * fdl[(pos - k) mod K] */
    cr_cpx *Y = n->acc;
    memset(Y, 0, sizeof(cr_cpx) * N);
    for (int k = 0; k < K; ++k) {
        int fi = fdl_pos_in - k;
        if (fi < 0) fi += K;
        const cr_cpx *F = &filt[(size_t)k * N];
        const cr_cpx *Xs = &fdl[(size_t)fi * N];
        for (int b = 0; b < N; ++b) {
            float fr = F[b].re, fii = F[b].im;
            float xr = Xs[b].re, xi = Xs[b].im;
            Y[b].re += fr * xr - fii * xi;
            Y[b].im += fr * xi + fii * xr;
        }
    }
    cr_fft(n, Y, 1);
    /* valid output = last CR_BLOCK samples (real part) */
    for (int i = 0; i < CR_BLOCK; ++i) outB[i] = Y[CR_BLOCK + i].re;
}

static void cr_process_block(ma_convreverb_node *n) {
    cr_convolver *c = n->conv[n->active];
    if (c == NULL || c->K < 1) {
        /* No filter — emit silence for this block. */
        unsigned long long base = n->wpos - (unsigned long long)CR_BLOCK + 1;
        for (int i = 0; i < CR_BLOCK; ++i) {
            unsigned idx = (unsigned)((base + i) & CR_RING_MASK);
            n->wetRingL[idx] = 0.0f; n->wetRingR[idx] = 0.0f;
        }
        memcpy(n->prevBlockL, n->inAccumL, sizeof(n->prevBlockL));
        memcpy(n->prevBlockR, n->inAccumR, sizeof(n->prevBlockR));
        return;
    }

    float outL[CR_BLOCK], outR[CR_BLOCK];
    int pos = c->fdl_pos;
    cr_process_channel(n, c, n->prevBlockL, n->inAccumL, c->filtL, c->fdlL, pos, outL);
    cr_process_channel(n, c, n->prevBlockR, n->inAccumR, c->filtR, c->fdlR, pos, outR);
    c->fdl_pos = (pos + 1) % c->K;

    /* Write wet block at absolute indices [base, base+B). The block's last
     * input sample is the current wpos; its first is wpos-B+1. */
    unsigned long long base = n->wpos - (unsigned long long)CR_BLOCK + 1;
    for (int i = 0; i < CR_BLOCK; ++i) {
        unsigned idx = (unsigned)((base + i) & CR_RING_MASK);
        n->wetRingL[idx] = outL[i];
        n->wetRingR[idx] = outR[i];
    }

    memcpy(n->prevBlockL, n->inAccumL, sizeof(n->prevBlockL));
    memcpy(n->prevBlockR, n->inAccumR, sizeof(n->prevBlockR));
}

static void cr_update_filters(ma_convreverb_node *n) {
    float sr = (float)(n->sampleRate ? n->sampleRate : 48000);
    float lc = cr_clamp(n->p_lowcut_hz, 10.0f, sr * 0.49f);
    float hc = cr_clamp(n->p_highcut_hz, 40.0f, sr * 0.49f);
    n->hp_R = expf(-2.0f * CR_PI * lc / sr);          /* one-pole HP pole */
    n->lp_a = 1.0f - expf(-2.0f * CR_PI * hc / sr);   /* one-pole LP coeff */
    n->filt_dirty = 0;
}

/* --- Audio callback ------------------------------------------------- */

static void cr_process_pcm_frames(
    ma_node *pNodeArg,
    const float **ppFramesIn,
    ma_uint32 *pFrameCountIn,
    float **ppFramesOut,
    ma_uint32 *pFrameCountOut)
{
    ma_convreverb_node *n = (ma_convreverb_node *)pNodeArg;
    const float *in  = ppFramesIn[0];
    float       *out = ppFramesOut[0];
    ma_uint32 frameCount = (*pFrameCountIn < *pFrameCountOut) ? *pFrameCountIn : *pFrameCountOut;

    if (n->filt_dirty) cr_update_filters(n);

    const float wet   = n->p_wet;
    const float dry   = n->p_dry;
    const float gain  = n->p_gain;
    const float width = n->p_width;
    const float hp_R  = n->hp_R;
    const float lp_a  = n->lp_a;

    /* current predelay in samples (clamped to ring) */
    int predSamp = (int)(n->p_predelay_ms * 0.001f * (float)n->sampleRate + 0.5f);
    if (predSamp < 0) predSamp = 0;
    if (predSamp > n->predCap - 1) predSamp = n->predCap - 1;

    for (ma_uint32 f = 0; f < frameCount; ++f) {
        float inL = in[f * 2 + 0];
        float inR = in[f * 2 + 1];

        /* stash dry (undelayed) for later aligned mix */
        unsigned widx = (unsigned)(n->wpos & CR_RING_MASK);
        n->dryRingL[widx] = inL;
        n->dryRingR[widx] = inR;

        /* push into predelay ring, read delayed sample for the wet path */
        n->predL[n->predPos] = inL;
        n->predR[n->predPos] = inR;
        int rpos = n->predPos - predSamp;
        if (rpos < 0) rpos += n->predCap;
        float dL = n->predL[rpos];
        float dR = n->predR[rpos];
        n->predPos = (n->predPos + 1) & n->predMask;

        /* Blend the wet input toward mono so the reverb tail doesn't pan with
         * the source. diffuse=1 → both channels excited by the same mono sum
         * (direction comes purely from the stereo IR → diffuse / enveloping);
         * diffuse=0 → channel-wise (wet follows the source's pan). The dry
         * passthrough below is untouched, so direct sound stays spatialized. */
        float diffuse = n->p_diffuse;
        float mono = (dL + dR) * 0.5f;
        float wInL = dL + (mono - dL) * diffuse;
        float wInR = dR + (mono - dR) * diffuse;

        /* accumulate predelayed (de-panned) input into the current block */
        n->inAccumL[n->accumFill] = wInL;
        n->inAccumR[n->accumFill] = wInR;
        n->accumFill++;
        if (n->accumFill >= CR_BLOCK) {
            cr_process_block(n);
            n->accumFill = 0;
        }

        /* emit output at a fixed CR_BLOCK latency */
        if (n->wpos >= (unsigned long long)CR_BLOCK) {
            unsigned long long r = n->wpos - (unsigned long long)CR_BLOCK;
            unsigned ridx = (unsigned)(r & CR_RING_MASK);
            float wL = n->wetRingL[ridx] * gain;
            float wR = n->wetRingR[ridx] * gain;

            /* wet tone shaping: highpass (lowcut) then lowpass (highcut) */
            float hpL = hp_R * (n->hp_yL + wL - n->hp_xL);
            n->hp_xL = wL; n->hp_yL = hpL;
            float hpR = hp_R * (n->hp_yR + wR - n->hp_xR);
            n->hp_xR = wR; n->hp_yR = hpR;
            n->lp_yL += lp_a * (hpL - n->lp_yL);
            n->lp_yR += lp_a * (hpR - n->lp_yR);
            float fL = n->lp_yL;
            float fR = n->lp_yR;

            /* stereo width (mid/side) */
            float mid  = (fL + fR) * 0.5f;
            float side = (fL - fR) * 0.5f * width;
            float outWL = mid + side;
            float outWR = mid - side;

            float dryL = n->dryRingL[ridx];
            float dryR = n->dryRingR[ridx];
            out[f * 2 + 0] = dry * dryL + wet * outWL;
            out[f * 2 + 1] = dry * dryR + wet * outWR;
        } else {
            out[f * 2 + 0] = dry * inL;
            out[f * 2 + 1] = dry * inR;
        }

        n->wpos++;
    }

    *pFrameCountIn  = frameCount;
    *pFrameCountOut = frameCount;
}

static ma_node_vtable cr_vtable = {
    cr_process_pcm_frames,
    NULL,   /* 1:1 */
    1, 1,
    0
};

/* --- Public API ----------------------------------------------------- */

MA_API ma_convreverb_node_config ma_convreverb_node_config_init(ma_uint32 channels, ma_uint32 sampleRate) {
    ma_convreverb_node_config cfg;
    memset(&cfg, 0, sizeof(cfg));
    cfg.channels = (channels == 0) ? 2 : channels;
    cfg.sampleRate = sampleRate;
    cfg.nodeConfig = ma_node_config_init();
    cfg.nodeConfig.vtable = &cr_vtable;
    static const ma_uint32 inChannels[1]  = {2};
    static const ma_uint32 outChannels[1] = {2};
    cfg.nodeConfig.pInputChannels  = inChannels;
    cfg.nodeConfig.pOutputChannels = outChannels;
    return cfg;
}

MA_API ma_convreverb_node *ma_convreverb_node_alloc(void) {
    ma_convreverb_node *p = (ma_convreverb_node *)ma_malloc(sizeof(ma_convreverb_node), NULL);
    if (p) memset(p, 0, sizeof(*p));
    return p;
}

MA_API void ma_convreverb_node_free(ma_convreverb_node *pNode) {
    if (pNode) ma_free(pNode, NULL);
}

MA_API ma_result ma_convreverb_node_init(
    ma_node_graph *pGraph,
    const ma_convreverb_node_config *pConfig,
    const ma_allocation_callbacks *pAllocCallbacks,
    ma_convreverb_node *pNode)
{
    if (pNode == NULL || pGraph == NULL || pConfig == NULL) return MA_INVALID_ARGS;
    if (pConfig->channels != 2) return MA_INVALID_ARGS;

    memset(pNode, 0, sizeof(*pNode));
    pNode->sampleRate = (pConfig->sampleRate == 0) ? 48000 : pConfig->sampleRate;

    ma_result r = ma_node_init(pGraph, &pConfig->nodeConfig, pAllocCallbacks, &pNode->base);
    if (r != MA_SUCCESS) return r;

    cr_fft_plan(pNode);

    /* default params */
    pNode->p_wet = 0.33f;
    pNode->p_dry = 1.0f;
    pNode->p_gain = 1.0f;
    pNode->p_width = 1.0f;
    pNode->p_predelay_ms = 0.0f;
    pNode->p_lowcut_hz = 20.0f;
    pNode->p_highcut_hz = 18000.0f;
    pNode->p_diffuse = 1.0f;  /* default: diffuse tail that doesn't pan with the source */
    pNode->p_decay = 1.0f;
    pNode->filt_dirty = 1;
    cr_update_filters(pNode);

    /* pre-delay ring sized for 250 ms. */
    int predNeed = (int)(0.25f * (float)pNode->sampleRate) + 2;
    pNode->predCap = cr_nextpow2(predNeed);
    pNode->predMask = pNode->predCap - 1;
    pNode->predL = (float *)calloc((size_t)pNode->predCap, sizeof(float));
    pNode->predR = (float *)calloc((size_t)pNode->predCap, sizeof(float));
    if (!pNode->predL || !pNode->predR) {
        free(pNode->predL); free(pNode->predR);
        ma_node_uninit(&pNode->base, pAllocCallbacks);
        return MA_OUT_OF_MEMORY;
    }

    /* Build the synthetic default IR so the node is immediately usable. */
    if (ma_convreverb_node_load_default_ir(pNode) != MA_SUCCESS) {
        free(pNode->predL); free(pNode->predR);
        ma_node_uninit(&pNode->base, pAllocCallbacks);
        return MA_ERROR;
    }

    return MA_SUCCESS;
}

MA_API void ma_convreverb_node_uninit(
    ma_convreverb_node *pNode,
    const ma_allocation_callbacks *pAllocCallbacks)
{
    if (pNode == NULL) return;
    ma_node_uninit(&pNode->base, pAllocCallbacks);
    for (int i = 0; i < 2; ++i) {
        if (pNode->conv[i]) {
            cr_convolver_free(pNode->conv[i]);
            free(pNode->conv[i]);
            pNode->conv[i] = NULL;
        }
    }
    free(pNode->rawL); free(pNode->rawR);
    free(pNode->predL); free(pNode->predR);
    pNode->rawL = pNode->rawR = NULL;
    pNode->predL = pNode->predR = NULL;
}

/* --- Param setters -------------------------------------------------- */

MA_API void ma_convreverb_node_set_wet     (ma_convreverb_node *p, float v) { if (p) p->p_wet  = cr_clamp(v, 0.0f, 1.0f); }
MA_API void ma_convreverb_node_set_dry     (ma_convreverb_node *p, float v) { if (p) p->p_dry  = cr_clamp(v, 0.0f, 1.0f); }
MA_API void ma_convreverb_node_set_predelay(ma_convreverb_node *p, float v) { if (p) p->p_predelay_ms = cr_clamp(v, 0.0f, 250.0f); }
MA_API void ma_convreverb_node_set_ir_gain (ma_convreverb_node *p, float v) { if (p) p->p_gain = cr_clamp(v, 0.0f, 4.0f); }
MA_API void ma_convreverb_node_set_width   (ma_convreverb_node *p, float v) { if (p) p->p_width = cr_clamp(v, 0.0f, 2.0f); }
MA_API void ma_convreverb_node_set_diffuse (ma_convreverb_node *p, float v) { if (p) p->p_diffuse = cr_clamp(v, 0.0f, 1.0f); }

MA_API void ma_convreverb_node_set_lowcut  (ma_convreverb_node *p, float v) {
    if (p) { p->p_lowcut_hz = v; p->filt_dirty = 1; }
}
MA_API void ma_convreverb_node_set_highcut (ma_convreverb_node *p, float v) {
    if (p) { p->p_highcut_hz = v; p->filt_dirty = 1; }
}

MA_API void ma_convreverb_node_set_decay(ma_convreverb_node *p, float v) {
    if (!p) return;
    p->p_decay = cr_clamp(v, 0.05f, 1.0f);
    cr_rebuild(p);   /* reshape the cached IR + republish */
}

/* --- IR management -------------------------------------------------- */

MA_API ma_result ma_convreverb_node_load_default_ir(ma_convreverb_node *pNode) {
    if (pNode == NULL) return MA_INVALID_ARGS;
    int frames = (int)(1.2f * (float)pNode->sampleRate);
    if (frames < CR_BLOCK) frames = CR_BLOCK;

    float *L = (float *)malloc(sizeof(float) * (size_t)frames);
    float *R = (float *)malloc(sizeof(float) * (size_t)frames);
    if (!L || !R) { free(L); free(R); return MA_OUT_OF_MEMORY; }

    float attackSamps = 0.005f * (float)pNode->sampleRate;
    for (int i = 0; i < frames; ++i) {
        float decayE = expf(-5.0f * (float)i / (float)frames);
        float atk = (attackSamps > 0.0f) ? fminf(1.0f, (float)i / attackSamps) : 1.0f;
        float env = decayE * atk;
        L[i] = cr_white() * env;
        R[i] = cr_white() * env;
    }

    free(pNode->rawL); free(pNode->rawR);
    pNode->rawL = L; pNode->rawR = R; pNode->raw_frames = frames;
    return cr_rebuild(pNode) ? MA_SUCCESS : MA_ERROR;
}

MA_API ma_result ma_convreverb_node_load_ir_file(ma_convreverb_node *pNode, const char *path) {
    if (pNode == NULL || path == NULL) return MA_INVALID_ARGS;

    ma_decoder_config dcfg = ma_decoder_config_init(ma_format_f32, 2, pNode->sampleRate);
    ma_decoder dec;
    ma_result r = ma_decoder_init_file(path, &dcfg, &dec);
    if (r != MA_SUCCESS) return r;

    int cap = (int)(CR_MAX_IR_SECONDS * (float)pNode->sampleRate);
    if (cap < CR_BLOCK) cap = CR_BLOCK;

    float *interleaved = (float *)malloc(sizeof(float) * (size_t)cap * 2);
    if (!interleaved) { ma_decoder_uninit(&dec); return MA_OUT_OF_MEMORY; }

    int total = 0;
    const ma_uint64 CHUNK = 4096;
    float chunk[4096 * 2];
    while (total < cap) {
        ma_uint64 want = CHUNK;
        if ((ma_uint64)(cap - total) < want) want = (ma_uint64)(cap - total);
        ma_uint64 got = 0;
        ma_result rr = ma_decoder_read_pcm_frames(&dec, chunk, want, &got);
        if (got > 0) {
            memcpy(interleaved + (size_t)total * 2, chunk, sizeof(float) * (size_t)got * 2);
            total += (int)got;
        }
        if (rr != MA_SUCCESS || got == 0) break;
    }
    ma_decoder_uninit(&dec);

    if (total < 1) { free(interleaved); return MA_ERROR; }

    /* deinterleave into planar */
    float *L = (float *)malloc(sizeof(float) * (size_t)total);
    float *R = (float *)malloc(sizeof(float) * (size_t)total);
    if (!L || !R) { free(L); free(R); free(interleaved); return MA_OUT_OF_MEMORY; }
    for (int i = 0; i < total; ++i) {
        L[i] = interleaved[(size_t)i * 2 + 0];
        R[i] = interleaved[(size_t)i * 2 + 1];
    }
    free(interleaved);

    free(pNode->rawL); free(pNode->rawR);
    pNode->rawL = L; pNode->rawR = R; pNode->raw_frames = total;
    return cr_rebuild(pNode) ? MA_SUCCESS : MA_ERROR;
}

MA_API ma_uint32 ma_convreverb_node_ir_frames(ma_convreverb_node *pNode) {
    return pNode ? (ma_uint32)pNode->raw_frames : 0;
}
