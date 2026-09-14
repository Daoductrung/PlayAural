/*
 * ma_eq.h — 3-band EQ (low shelf + mid peak + high shelf) as an ma_node.
 *
 * Stereo in, stereo out. Per-band gain in dB, fixed crossover frequencies.
 * Biquad filters, no saturation or clipping — pure linear EQ.
 */

#ifndef MA_EQ_H
#define MA_EQ_H

#include "miniaudio.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ma_eq_node_config {
    ma_node_config nodeConfig;
    ma_uint32 channels;     /* Must be 2. */
    ma_uint32 sampleRate;
} ma_eq_node_config;

typedef struct ma_eq_node ma_eq_node;

MA_API ma_eq_node_config ma_eq_node_config_init(ma_uint32 channels, ma_uint32 sampleRate);

MA_API ma_eq_node *ma_eq_node_alloc(void);
MA_API void        ma_eq_node_free(ma_eq_node *pNode);

MA_API ma_result ma_eq_node_init(
    ma_node_graph *pGraph,
    const ma_eq_node_config *pConfig,
    const ma_allocation_callbacks *pAllocCallbacks,
    ma_eq_node *pNode);

MA_API void ma_eq_node_uninit(
    ma_eq_node *pNode,
    const ma_allocation_callbacks *pAllocCallbacks);

/* Per-band gain in dB. Positive = boost, negative = cut. ±24 dB range. */
MA_API void ma_eq_node_set_low_gain (ma_eq_node *pNode, float db);
MA_API void ma_eq_node_set_mid_gain (ma_eq_node *pNode, float db);
MA_API void ma_eq_node_set_high_gain(ma_eq_node *pNode, float db);

/* Cutoff / center frequencies (Hz). */
MA_API void ma_eq_node_set_low_freq (ma_eq_node *pNode, float hz);
MA_API void ma_eq_node_set_mid_freq (ma_eq_node *pNode, float hz);
MA_API void ma_eq_node_set_high_freq(ma_eq_node *pNode, float hz);

/* Mid-band Q (bandwidth). Default 1.0. */
MA_API void ma_eq_node_set_mid_q(ma_eq_node *pNode, float q);

#ifdef __cplusplus
}
#endif

#endif
