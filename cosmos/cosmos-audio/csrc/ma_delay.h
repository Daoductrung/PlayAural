/*
 * ma_delay.h — stereo delay / echo as an ma_node.
 *
 * Stereo in, stereo out. A feedback delay line per channel with wet/dry mix.
 * Layout mirrors ma_eq.c so it drops into the same effect-chain plumbing.
 */

#ifndef MA_DELAY_H
#define MA_DELAY_H

#include "miniaudio.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ma_delay_fx_config {
    ma_node_config nodeConfig;
    ma_uint32 channels;     /* Must be 2. */
    ma_uint32 sampleRate;
} ma_delay_fx_config;

typedef struct ma_delay_fx ma_delay_fx;

MA_API ma_delay_fx_config ma_delay_fx_config_init(ma_uint32 channels, ma_uint32 sampleRate);

MA_API ma_delay_fx *ma_delay_fx_alloc(void);
MA_API void         ma_delay_fx_free(ma_delay_fx *pNode);

MA_API ma_result ma_delay_fx_init(
    ma_node_graph *pGraph,
    const ma_delay_fx_config *pConfig,
    const ma_allocation_callbacks *pAllocCallbacks,
    ma_delay_fx *pNode);

MA_API void ma_delay_fx_uninit(
    ma_delay_fx *pNode,
    const ma_allocation_callbacks *pAllocCallbacks);

/* Delay time in milliseconds (1 .. 2000). */
MA_API void ma_delay_fx_set_delay_ms(ma_delay_fx *pNode, float ms);
/* Feedback amount (0 .. 0.95) — how much of the echo feeds back in. */
MA_API void ma_delay_fx_set_feedback(ma_delay_fx *pNode, float fb);
/* Wet (delayed) level (0 .. 1). */
MA_API void ma_delay_fx_set_wet(ma_delay_fx *pNode, float wet);
/* Dry (direct) level (0 .. 1). */
MA_API void ma_delay_fx_set_dry(ma_delay_fx *pNode, float dry);

#ifdef __cplusplus
}
#endif

#endif
