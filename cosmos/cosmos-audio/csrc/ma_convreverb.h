/*
 * ma_convreverb.h — Convolution (impulse-response) reverb node for miniaudio.
 *
 * Replaces the old algorithmic Freeverb node. Stereo in, stereo out. Uses a
 * uniformly-partitioned overlap-save (UPOLS) FFT convolution so arbitrarily
 * long impulse responses run in real time at a small, fixed latency.
 *
 * An impulse response can be loaded from any audio file miniaudio can decode
 * (wav/ogg/flac/mp3); it is resampled to the engine sample rate and folded to
 * stereo automatically. A synthetic decaying-noise IR is generated at init so
 * the node is usable out of the box.
 *
 * All loading / decay-reshaping work happens on the calling (control) thread
 * and is published to the audio thread via an atomic double-buffer swap, so
 * `load_ir` / `set_decay` are safe to call while audio is running.
 *
 * Per-sample parameters (wet, dry, pre-delay, ir gain, width, low/high cut)
 * are applied live without a rebuild.
 */

#ifndef MA_CONVREVERB_H
#define MA_CONVREVERB_H

#include "miniaudio.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ma_convreverb_node_config {
    ma_node_config nodeConfig;
    ma_uint32 channels;    /* Must be 2 (stereo). */
    ma_uint32 sampleRate;  /* Engine sample rate. IRs are resampled to this. */
} ma_convreverb_node_config;

typedef struct ma_convreverb_node ma_convreverb_node;

MA_API ma_convreverb_node_config ma_convreverb_node_config_init(ma_uint32 channels, ma_uint32 sampleRate);

/* Heap helpers — Rust doesn't know the real node size. */
MA_API ma_convreverb_node *ma_convreverb_node_alloc(void);
MA_API void                ma_convreverb_node_free(ma_convreverb_node *pNode);

MA_API ma_result ma_convreverb_node_init(
    ma_node_graph *pGraph,
    const ma_convreverb_node_config *pConfig,
    const ma_allocation_callbacks *pAllocCallbacks,
    ma_convreverb_node *pNode);

MA_API void ma_convreverb_node_uninit(
    ma_convreverb_node *pNode,
    const ma_allocation_callbacks *pAllocCallbacks);

/* --- Live per-sample parameters ------------------------------------- */
MA_API void ma_convreverb_node_set_wet     (ma_convreverb_node *pNode, float wet);      /* [0,1]  reverb tail level */
MA_API void ma_convreverb_node_set_dry     (ma_convreverb_node *pNode, float dry);      /* [0,1]  direct level */
MA_API void ma_convreverb_node_set_predelay(ma_convreverb_node *pNode, float ms);       /* [0,250] ms before the wet onset */
MA_API void ma_convreverb_node_set_ir_gain (ma_convreverb_node *pNode, float gain);     /* [0,4]  wet makeup gain */
MA_API void ma_convreverb_node_set_width   (ma_convreverb_node *pNode, float width);    /* [0,2]  stereo width of the wet */
MA_API void ma_convreverb_node_set_lowcut  (ma_convreverb_node *pNode, float hz);       /* high-pass on the wet */
MA_API void ma_convreverb_node_set_highcut (ma_convreverb_node *pNode, float hz);       /* low-pass on the wet */
/* How much the wet input is summed to mono before convolution. 0 = wet follows
 * the source's pan (channel-wise); 1 = fully mono send → diffuse, enveloping
 * tail that does NOT pan with the source. */
MA_API void ma_convreverb_node_set_diffuse (ma_convreverb_node *pNode, float amt);       /* [0,1] */

/* --- Rebuild-triggering parameter ----------------------------------- */
/* Exponential tail-shaping applied to the loaded IR. 1.0 = unchanged,
 * smaller = shorter/tighter tail. Rebuilds the partitioned filter. */
MA_API void ma_convreverb_node_set_decay   (ma_convreverb_node *pNode, float decay);

/* --- Impulse-response management (control thread) ------------------- */
/* Decode `path`, resample to the engine SR, fold to stereo, and rebuild the
 * partitioned filter. Returns MA_SUCCESS or a miniaudio error. */
MA_API ma_result ma_convreverb_node_load_ir_file(ma_convreverb_node *pNode, const char *path);
/* Regenerate the built-in synthetic decaying-noise IR. */
MA_API ma_result ma_convreverb_node_load_default_ir(ma_convreverb_node *pNode);
/* Length, in frames, of the currently loaded IR (post-resample). */
MA_API ma_uint32 ma_convreverb_node_ir_frames(ma_convreverb_node *pNode);

#ifdef __cplusplus
}
#endif

#endif /* MA_CONVREVERB_H */
