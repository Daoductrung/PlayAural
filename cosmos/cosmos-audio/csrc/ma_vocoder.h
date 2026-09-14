/*
 * ma_vocoder.h — single-input channel vocoder as an ma_node.
 *
 * The incoming audio is the *modulator*: it's split into N log-spaced bands,
 * each band's amplitude envelope is followed, and those envelopes shape an
 * internally-synthesized *carrier* (sawtooth / pulse / noise / supersaw) split
 * through a parallel band bank whose centers can be formant-shifted. The carrier
 * pitch can be randomized (toggle + rate + depth), detuned across the stereo
 * field (spread), and unvoiced highs can be passed through (sibilance) for
 * clarity. Stereo in/out; layout mirrors ma_eq.c.
 */

#ifndef MA_VOCODER_H
#define MA_VOCODER_H

#include "miniaudio.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    MA_VOCODER_CARRIER_SAW      = 0,
    MA_VOCODER_CARRIER_PULSE    = 1,
    MA_VOCODER_CARRIER_NOISE    = 2,
    MA_VOCODER_CARRIER_SUPERSAW = 3
} ma_vocoder_carrier;

typedef struct ma_vocoder_node_config {
    ma_node_config nodeConfig;
    ma_uint32 channels;     /* Must be 2. */
    ma_uint32 sampleRate;
} ma_vocoder_node_config;

typedef struct ma_vocoder_node ma_vocoder_node;

MA_API ma_vocoder_node_config ma_vocoder_node_config_init(ma_uint32 channels, ma_uint32 sampleRate);

MA_API ma_vocoder_node *ma_vocoder_node_alloc(void);
MA_API void             ma_vocoder_node_free(ma_vocoder_node *pNode);

MA_API ma_result ma_vocoder_node_init(
    ma_node_graph *pGraph,
    const ma_vocoder_node_config *pConfig,
    const ma_allocation_callbacks *pAllocCallbacks,
    ma_vocoder_node *pNode);

MA_API void ma_vocoder_node_uninit(
    ma_vocoder_node *pNode,
    const ma_allocation_callbacks *pAllocCallbacks);

/* Number of analysis/synthesis bands (4 .. 32). */
MA_API void ma_vocoder_node_set_bands(ma_vocoder_node *pNode, int bands);
/* Carrier waveform — one of ma_vocoder_carrier. */
MA_API void ma_vocoder_node_set_carrier(ma_vocoder_node *pNode, int carrier);
/* Carrier pitch in Hz for tonal carriers: 40 .. 800. */
MA_API void ma_vocoder_node_set_carrier_freq(ma_vocoder_node *pNode, float hz);
/* Envelope follower attack time in ms (0.1 .. 100). */
MA_API void ma_vocoder_node_set_attack(ma_vocoder_node *pNode, float ms);
/* Envelope follower release time in ms (1 .. 500). */
MA_API void ma_vocoder_node_set_release(ma_vocoder_node *pNode, float ms);
/* Wet (vocoded) level (0 .. 1). */
MA_API void ma_vocoder_node_set_wet(ma_vocoder_node *pNode, float wet);
/* Dry (direct) level (0 .. 1). */
MA_API void ma_vocoder_node_set_dry(ma_vocoder_node *pNode, float dry);

/* --- Advanced ------------------------------------------------------- */

/* Carrier-pitch randomization on/off (non-zero = on). */
MA_API void ma_vocoder_node_set_rand(ma_vocoder_node *pNode, int on);
/* How often a new random pitch is chosen, in Hz (0.1 .. 30). */
MA_API void ma_vocoder_node_set_rand_rate(ma_vocoder_node *pNode, float hz);
/* Random pitch spread in octaves each way (0 .. 4). */
MA_API void ma_vocoder_node_set_rand_depth(ma_vocoder_node *pNode, float octaves);
/* Formant shift — scales the carrier band centers vs the modulator (0.25 .. 4). */
MA_API void ma_vocoder_node_set_formant(ma_vocoder_node *pNode, float factor);
/* Stereo carrier detune amount (0 .. 1). */
MA_API void ma_vocoder_node_set_spread(ma_vocoder_node *pNode, float spread);
/* Unvoiced high-frequency passthrough for consonant clarity (0 .. 1). */
MA_API void ma_vocoder_node_set_sibilance(ma_vocoder_node *pNode, float amt);

#ifdef __cplusplus
}
#endif

#endif
