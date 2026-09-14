//! Steam Audio (Phonon) integration for HRTF binaural processing.
//!
//! This module provides bindings to the miniaudio_phonon.c integration code
//! which creates binaural nodes that plug into miniaudio's audio graph.

use miniaudio_sys::{
    ma_allocation_callbacks, ma_bool32, ma_node_graph, ma_result, ma_uint32, MA_SUCCESS, MA_TRUE,
};
use steamaudio_sys::{IPLAudioSettings, IPLContext, IPLHRTF};
use std::ptr;
use std::sync::atomic::{AtomicBool, Ordering};

use crate::error::AudioError;

// FFI bindings to miniaudio_phonon.c
#[repr(C)]
pub struct PhononBinauralNodeConfig {
    pub node_config: miniaudio_sys::ma_node_config,
    pub channels_in: ma_uint32,
    pub ipl_audio_settings: IPLAudioSettings,
    pub ipl_context: IPLContext,
    pub ipl_hrtf: IPLHRTF,
}

#[repr(C)]
pub struct PhononBinauralNode {
    // Opaque - actual struct is defined in C
    _data: [u8; 512], // Placeholder, actual size determined by C
}

extern "C" {
    fn ma_phonon_init(sample_rate: ma_uint32, frame_size: ma_uint32) -> ma_result;
    fn ma_phonon_uninit();
    fn ma_phonon_get_context() -> IPLContext;
    fn ma_phonon_get_hrtf() -> IPLHRTF;
    fn ma_phonon_get_audio_settings() -> IPLAudioSettings;
    fn ma_phonon_is_initialized() -> ma_bool32;

    fn ma_phonon_binaural_node_config_init(
        channels_in: ma_uint32,
        ipl_audio_settings: IPLAudioSettings,
        ipl_context: IPLContext,
        ipl_hrtf: IPLHRTF,
    ) -> PhononBinauralNodeConfig;

    fn ma_phonon_binaural_node_init(
        node_graph: *mut ma_node_graph,
        config: *const PhononBinauralNodeConfig,
        allocation_callbacks: *const ma_allocation_callbacks,
        binaural_node: *mut PhononBinauralNode,
    ) -> ma_result;

    fn ma_phonon_binaural_node_uninit(
        binaural_node: *mut PhononBinauralNode,
        allocation_callbacks: *const ma_allocation_callbacks,
    );

    fn ma_phonon_binaural_node_set_direction(
        binaural_node: *mut PhononBinauralNode,
        x: f32,
        y: f32,
        z: f32,
        distance: f32,
    ) -> ma_result;

    #[allow(dead_code)]
    fn ma_phonon_binaural_node_set_spatial_blend_max_distance(
        binaural_node: *mut PhononBinauralNode,
        max_distance: f32,
    ) -> ma_result;

    fn ma_phonon_binaural_node_alloc() -> *mut PhononBinauralNode;
    fn ma_phonon_binaural_node_free(node: *mut PhononBinauralNode);
}

// Track global phonon initialization
static PHONON_INITIALIZED: AtomicBool = AtomicBool::new(false);

/// Initialize the global Steam Audio context.
///
/// This should be called once when creating the audio engine.
/// Returns Ok(true) if initialized successfully, Ok(false) if already initialized.
pub fn phonon_init(sample_rate: u32, frame_size: u32) -> Result<bool, AudioError> {
    if PHONON_INITIALIZED.load(Ordering::SeqCst) {
        return Ok(false);
    }

    let result = unsafe { ma_phonon_init(sample_rate, frame_size) };
    if result == MA_SUCCESS {
        PHONON_INITIALIZED.store(true, Ordering::SeqCst);
        Ok(true)
    } else {
        Err(AudioError::PhononInitFailed)
    }
}

/// Uninitialize the global Steam Audio context.
pub fn phonon_uninit() {
    if PHONON_INITIALIZED.load(Ordering::SeqCst) {
        unsafe { ma_phonon_uninit() };
        PHONON_INITIALIZED.store(false, Ordering::SeqCst);
    }
}

/// Check if Steam Audio is initialized.
pub fn phonon_is_initialized() -> bool {
    unsafe { ma_phonon_is_initialized() == MA_TRUE }
}

/// Get the global Steam Audio context.
pub fn phonon_get_context() -> IPLContext {
    unsafe { ma_phonon_get_context() }
}

/// Get the global HRTF.
pub fn phonon_get_hrtf() -> IPLHRTF {
    unsafe { ma_phonon_get_hrtf() }
}

/// Get the audio settings used by Steam Audio.
pub fn phonon_get_audio_settings() -> IPLAudioSettings {
    unsafe { ma_phonon_get_audio_settings() }
}

/// A binaural node that applies HRTF processing to audio.
///
/// This node is inserted into the miniaudio audio graph between a sound
/// and the endpoint to provide 3D audio spatialization via Steam Audio.
pub struct BinauralNode {
    node: *mut PhononBinauralNode,
    initialized: bool,
}

impl BinauralNode {
    /// Create a new binaural node.
    ///
    /// # Arguments
    /// * `node_graph` - The miniaudio node graph to attach to
    /// * `channels_in` - Number of input channels (1 or 2)
    pub fn new(node_graph: *mut ma_node_graph, channels_in: u32) -> Result<Self, AudioError> {
        if !phonon_is_initialized() {
            return Err(AudioError::PhononInitFailed);
        }

        let node = unsafe { ma_phonon_binaural_node_alloc() };
        if node.is_null() {
            return Err(AudioError::AllocationFailed);
        }

        let config = unsafe {
            ma_phonon_binaural_node_config_init(
                channels_in,
                phonon_get_audio_settings(),
                phonon_get_context(),
                phonon_get_hrtf(),
            )
        };

        let result =
            unsafe { ma_phonon_binaural_node_init(node_graph, &config, ptr::null(), node) };

        if result != MA_SUCCESS {
            unsafe { ma_phonon_binaural_node_free(node) };
            return Err(AudioError::BinauralEffectFailed);
        }

        Ok(Self {
            node,
            initialized: true,
        })
    }

    /// Get the raw node pointer for audio graph operations.
    pub fn as_ptr(&self) -> *mut PhononBinauralNode {
        self.node
    }

    /// Set the direction of the sound source relative to the listener.
    ///
    /// The direction should be in Steam Audio coordinates:
    /// - X: Right (+) / Left (-)
    /// - Y: Up (+) / Down (-)
    /// - Z: Back (+) / Front (-)
    ///
    /// The direction vector should be normalized.
    pub fn set_direction(&mut self, x: f32, y: f32, z: f32, distance: f32) {
        if self.initialized {
            unsafe {
                ma_phonon_binaural_node_set_direction(self.node, x, y, z, distance);
            }
        }
    }

    /// Set the maximum distance for spatial blend.
    ///
    /// At distances beyond this, the HRTF effect is at full strength.
    /// At closer distances, the effect is blended with the original signal.
    #[allow(dead_code)]
    pub fn set_spatial_blend_max_distance(&mut self, max_distance: f32) {
        if self.initialized {
            unsafe {
                ma_phonon_binaural_node_set_spatial_blend_max_distance(self.node, max_distance);
            }
        }
    }
}

impl Drop for BinauralNode {
    fn drop(&mut self) {
        if self.initialized && !self.node.is_null() {
            unsafe {
                ma_phonon_binaural_node_uninit(self.node, ptr::null());
                ma_phonon_binaural_node_free(self.node);
            }
        }
    }
}

// BinauralNode contains raw pointers but the node is tied to a specific audio graph
// and should only be used from the thread that created it.
// We don't implement Send/Sync to prevent cross-thread usage.
