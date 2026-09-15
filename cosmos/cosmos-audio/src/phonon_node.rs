//! Steam Audio (Phonon) integration for HRTF binaural processing.
//!
//! This module provides bindings to the miniaudio_phonon.c integration code
//! which creates binaural nodes that plug into miniaudio's audio graph.

use miniaudio_sys::{
    ma_allocation_callbacks, ma_bool32, ma_node_graph, ma_result, ma_uint32, MA_SUCCESS, MA_TRUE,
};
use std::ptr;
use std::sync::Mutex;
use steamaudio_sys::{
    IPLAudioSettings, IPLContext, IPLHRTFInterpolation,
    IPLHRTFInterpolation_IPL_HRTFINTERPOLATION_BILINEAR,
    IPLHRTFInterpolation_IPL_HRTFINTERPOLATION_NEAREST, IPLHRTF,
};

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
    _private: [u8; 0],
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

    fn ma_phonon_binaural_node_set_parameters(
        binaural_node: *mut PhononBinauralNode,
        x: f32,
        y: f32,
        z: f32,
        spatial_blend: f32,
        interpolation: IPLHRTFInterpolation,
    ) -> ma_result;

    fn ma_phonon_binaural_node_alloc() -> *mut PhononBinauralNode;
    fn ma_phonon_binaural_node_free(node: *mut PhononBinauralNode);
}

static PHONON_LIFECYCLE: Mutex<()> = Mutex::new(());

/// Steam Audio processing block size. The same value is supplied to the
/// miniaudio engine period and the HRTF context, so they cannot drift apart.
pub const HRTF_FRAME_SIZE: u32 = 512;

/// Direction interpolation used when a source falls between measured HRTF
/// points. Bilinear is the smooth, high-quality choice for moving sources;
/// nearest is retained as an explicit lower-CPU option.
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum HrtfInterpolation {
    Nearest,
    #[default]
    Bilinear,
}

impl HrtfInterpolation {
    fn as_steam_audio(self) -> IPLHRTFInterpolation {
        match self {
            Self::Nearest => IPLHRTFInterpolation_IPL_HRTFINTERPOLATION_NEAREST,
            Self::Bilinear => IPLHRTFInterpolation_IPL_HRTFINTERPOLATION_BILINEAR,
        }
    }
}

/// Acquire the shared Steam Audio context for one audio engine.
///
/// Every successful acquisition must be paired with [`phonon_uninit`]. Engines
/// must use identical sample-rate and frame-size settings while they coexist.
pub fn phonon_init(sample_rate: u32, frame_size: u32) -> Result<(), AudioError> {
    let _guard = PHONON_LIFECYCLE
        .lock()
        .unwrap_or_else(|poisoned| poisoned.into_inner());
    let result = unsafe { ma_phonon_init(sample_rate, frame_size) };
    if result == MA_SUCCESS {
        Ok(())
    } else {
        Err(AudioError::PhononInitFailed)
    }
}

/// Uninitialize the global Steam Audio context.
pub fn phonon_uninit() {
    let _guard = PHONON_LIFECYCLE
        .lock()
        .unwrap_or_else(|poisoned| poisoned.into_inner());
    unsafe { ma_phonon_uninit() };
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
    direction: (f32, f32, f32),
    spatial_blend: f32,
    interpolation: HrtfInterpolation,
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
            direction: (0.0, 0.0, -1.0),
            spatial_blend: 1.0,
            interpolation: HrtfInterpolation::default(),
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
    /// Set the dry/HRTF blend (0 = direct, 1 = fully binaural).
    pub fn set_spatial_blend(&mut self, spatial_blend: f32) {
        if spatial_blend.is_finite() {
            self.spatial_blend = spatial_blend.clamp(0.0, 1.0);
            self.apply_parameters();
        }
    }

    /// Set HRTF measurement interpolation quality.
    pub fn set_interpolation(&mut self, interpolation: HrtfInterpolation) {
        self.interpolation = interpolation;
        self.apply_parameters();
    }

    /// Publish direction and blend together as one coherent audio-thread update.
    pub fn set_spatial_parameters(&mut self, x: f32, y: f32, z: f32, spatial_blend: f32) {
        if x.is_finite() && y.is_finite() && z.is_finite() && spatial_blend.is_finite() {
            self.direction = (x, y, z);
            self.spatial_blend = spatial_blend.clamp(0.0, 1.0);
            self.apply_parameters();
        }
    }

    fn apply_parameters(&mut self) {
        if !self.initialized {
            return;
        }
        let (x, y, z) = self.direction;
        unsafe {
            ma_phonon_binaural_node_set_parameters(
                self.node,
                x,
                y,
                z,
                self.spatial_blend,
                self.interpolation.as_steam_audio(),
            );
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

// BinauralNode is not Send/Sync on its own. Sound's guarded Send implementation
// owns the cross-thread contract: graph access is serialized by SoundRef and
// callback-visible parameters are published through the C11 atomic snapshot.
