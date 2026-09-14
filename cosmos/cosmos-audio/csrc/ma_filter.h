/*
 * ma_filter.h — multimode biquad filter as an ma_node.
 *
 * Stereo in, stereo out. One RBJ biquad per channel with a switchable mode
 * (lowpass / highpass / bandpass / notch / peak / low shelf / high shelf /
 * allpass), a cutoff/center frequency, a resonance (Q), and a gain (dB) used
 * by the peak and shelf modes. Designed to mirror ma_eq.c's node layout so it
 * slots into the same effect-chain plumbing.
 */

#ifndef MA_FILTER_H
#define MA_FILTER_H

#include "miniaudio.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Filter modes. Kept in sync with the Rust/Python side. */
typedef enum {
    MA_FILTER_LOWPASS   = 0,
    MA_FILTER_HIGHPASS  = 1,
    MA_FILTER_BANDPASS  = 2,
    MA_FILTER_NOTCH     = 3,
    MA_FILTER_PEAK      = 4,
    MA_FILTER_LOWSHELF  = 5,
    MA_FILTER_HIGHSHELF = 6,
    MA_FILTER_ALLPASS   = 7
} ma_filter_mode;

typedef struct ma_filter_node_config {
    ma_node_config nodeConfig;
    ma_uint32 channels;     /* Must be 2. */
    ma_uint32 sampleRate;
} ma_filter_node_config;

typedef struct ma_filter_node ma_filter_node;

MA_API ma_filter_node_config ma_filter_node_config_init(ma_uint32 channels, ma_uint32 sampleRate);

MA_API ma_filter_node *ma_filter_node_alloc(void);
MA_API void            ma_filter_node_free(ma_filter_node *pNode);

MA_API ma_result ma_filter_node_init(
    ma_node_graph *pGraph,
    const ma_filter_node_config *pConfig,
    const ma_allocation_callbacks *pAllocCallbacks,
    ma_filter_node *pNode);

MA_API void ma_filter_node_uninit(
    ma_filter_node *pNode,
    const ma_allocation_callbacks *pAllocCallbacks);

/* Mode — one of ma_filter_mode (clamped to the valid range). */
MA_API void ma_filter_node_set_mode(ma_filter_node *pNode, int mode);
/* Cutoff / center frequency in Hz (20 .. 20000). */
MA_API void ma_filter_node_set_freq(ma_filter_node *pNode, float hz);
/* Resonance / Q (0.1 .. 24). */
MA_API void ma_filter_node_set_q(ma_filter_node *pNode, float q);
/* Gain in dB for peak / shelf modes (-24 .. 24); ignored by other modes. */
MA_API void ma_filter_node_set_gain(ma_filter_node *pNode, float db);

#ifdef __cplusplus
}
#endif

#endif
