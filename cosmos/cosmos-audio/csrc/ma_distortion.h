/*
 * ma_distortion.h — waveshaping distortion / overdrive as an ma_node.
 *
 * Stereo in, stereo out. Pre-gain (drive) into a tanh saturator, a one-pole
 * low-pass "tone" control on the shaped signal, then a wet/dry mix. Layout
 * mirrors ma_eq.c so it slots into the same effect-chain plumbing.
 */

#ifndef MA_DISTORTION_H
#define MA_DISTORTION_H

#include "miniaudio.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ma_distortion_node_config {
    ma_node_config nodeConfig;
    ma_uint32 channels;     /* Must be 2. */
    ma_uint32 sampleRate;
} ma_distortion_node_config;

typedef struct ma_distortion_node ma_distortion_node;

MA_API ma_distortion_node_config ma_distortion_node_config_init(ma_uint32 channels, ma_uint32 sampleRate);

MA_API ma_distortion_node *ma_distortion_node_alloc(void);
MA_API void                ma_distortion_node_free(ma_distortion_node *pNode);

MA_API ma_result ma_distortion_node_init(
    ma_node_graph *pGraph,
    const ma_distortion_node_config *pConfig,
    const ma_allocation_callbacks *pAllocCallbacks,
    ma_distortion_node *pNode);

MA_API void ma_distortion_node_uninit(
    ma_distortion_node *pNode,
    const ma_allocation_callbacks *pAllocCallbacks);

/* Pre-gain into the saturator (1 .. 50). Higher = more crunch. */
MA_API void ma_distortion_node_set_drive(ma_distortion_node *pNode, float drive);
/* Tone — one-pole low-pass cutoff on the shaped signal in Hz (200 .. 18000). */
MA_API void ma_distortion_node_set_tone(ma_distortion_node *pNode, float hz);
/* Wet (distorted) level (0 .. 1). */
MA_API void ma_distortion_node_set_wet(ma_distortion_node *pNode, float wet);
/* Dry (clean) level (0 .. 1). */
MA_API void ma_distortion_node_set_dry(ma_distortion_node *pNode, float dry);

#ifdef __cplusplus
}
#endif

#endif
