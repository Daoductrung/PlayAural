/*
 * ma_disperser.h — phase disperser (cascaded allpass) as an ma_node.
 *
 * Stereo in / stereo out. A chain of biquad allpass filters centered at a
 * user-tunable frequency smears transients across time (the "laser" /
 * "disperser" effect popularized by the Kilohearts plugin). Louder on
 * percussive material than tonal.
 */

#ifndef MA_DISPERSER_H
#define MA_DISPERSER_H

#include "miniaudio.h"

#ifdef __cplusplus
extern "C" {
#endif

#define MA_DISPERSER_MAX_STAGES 32

typedef struct ma_disperser_node_config {
    ma_node_config nodeConfig;
    ma_uint32 channels;     /* Must be 2. */
    ma_uint32 sampleRate;
} ma_disperser_node_config;

typedef struct ma_disperser_node ma_disperser_node;

MA_API ma_disperser_node_config ma_disperser_node_config_init(ma_uint32 channels, ma_uint32 sampleRate);

MA_API ma_disperser_node *ma_disperser_node_alloc(void);
MA_API void               ma_disperser_node_free(ma_disperser_node *pNode);

MA_API ma_result ma_disperser_node_init(
    ma_node_graph *pGraph,
    const ma_disperser_node_config *pConfig,
    const ma_allocation_callbacks *pAllocCallbacks,
    ma_disperser_node *pNode);

MA_API void ma_disperser_node_uninit(
    ma_disperser_node *pNode,
    const ma_allocation_callbacks *pAllocCallbacks);

/* Center freq (Hz) where maximum phase rotation occurs. */
MA_API void ma_disperser_node_set_freq   (ma_disperser_node *pNode, float hz);
/* Q / bandwidth of each allpass. Higher = narrower, more tonal ring. */
MA_API void ma_disperser_node_set_q      (ma_disperser_node *pNode, float q);
/* Number of cascaded allpass stages (1..32). More = stronger dispersion. */
MA_API void ma_disperser_node_set_stages (ma_disperser_node *pNode, int stages);

#ifdef __cplusplus
}
#endif

#endif
