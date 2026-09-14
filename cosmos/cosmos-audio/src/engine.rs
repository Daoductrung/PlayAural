//! Audio engine wrapper around miniaudio.
//!
//! Manages the audio device, listener position, and HRTF initialization.

use miniaudio_sys::{
    ma_engine, ma_engine_get_node_graph, ma_engine_get_sample_rate,
    ma_engine_listener_set_position, ma_node_graph, MA_SUCCESS,
};

use crate::error::AudioError;
use crate::phonon_node;

// FFI for helper functions in miniaudio_impl.c
extern "C" {
    fn ma_engine_alloc() -> *mut ma_engine;
    fn ma_engine_free(engine: *mut ma_engine);
    fn ma_engine_init_with_caching(engine: *mut ma_engine) -> i32;
    fn ma_engine_uninit_with_caching(engine: *mut ma_engine);
    fn ma_engine_get_endpoint(engine: *mut ma_engine) -> *mut std::ffi::c_void;
}

/// Audio engine that manages the miniaudio backend and listener state.
///
/// Created and owned by `SoundManager` - do not instantiate directly.
pub struct AudioEngine {
    engine: *mut ma_engine,
    initialized: bool,
    hrtf_initialized: bool,

    // Listener position and orientation for 3D audio
    listener_x: f32,
    listener_y: f32,
    listener_z: f32,
    listener_angle: f32, // Degrees, unit circle: 0 = +X (east), 90 = +Y (north/forward)
}

impl AudioEngine {
    /// Initialize the audio engine.
    pub fn new() -> Result<Self, AudioError> {
        let engine = unsafe { ma_engine_alloc() };
        if engine.is_null() {
            return Err(AudioError::AllocationFailed);
        }

        // Initialize with resource manager for automatic sound caching
        let result = unsafe { ma_engine_init_with_caching(engine) };
        if result != MA_SUCCESS {
            unsafe { ma_engine_free(engine) };
            return Err(AudioError::EngineInitFailed);
        }

        // Initialize Steam Audio for HRTF
        let sample_rate = unsafe { ma_engine_get_sample_rate(engine) };
        // Use 512 frame size - must match engine periodSizeInFrames
        let hrtf_initialized = phonon_node::phonon_init(sample_rate, 512).unwrap_or(false);

        Ok(Self {
            engine,
            initialized: true,
            hrtf_initialized,
            listener_x: 0.0,
            listener_y: 0.0,
            listener_z: 0.0,
            listener_angle: 0.0,
        })
    }

    /// Get the underlying miniaudio engine pointer.
    pub fn as_ptr(&self) -> *mut ma_engine {
        self.engine
    }

    /// Get the audio node graph for custom audio routing.
    pub fn get_node_graph(&self) -> *mut ma_node_graph {
        unsafe { ma_engine_get_node_graph(self.engine) }
    }

    /// Get the audio endpoint for node attachment.
    pub fn get_endpoint(&self) -> *mut std::ffi::c_void {
        unsafe { ma_engine_get_endpoint(self.engine) }
    }

    /// Check if HRTF is available.
    pub fn is_hrtf_available(&self) -> bool {
        self.hrtf_initialized
    }

    /// Set the 3D listener position.
    pub fn set_listener_position(&mut self, x: f32, y: f32, z: f32) {
        self.listener_x = x;
        self.listener_y = y;
        self.listener_z = z;
        if self.initialized {
            unsafe {
                ma_engine_listener_set_position(self.engine, 0, x, y, z);
            }
        }
    }

    /// Get listener X position.
    pub fn listener_x(&self) -> f32 {
        self.listener_x
    }

    /// Get listener Y position.
    pub fn listener_y(&self) -> f32 {
        self.listener_y
    }

    /// Get listener Z position.
    pub fn listener_z(&self) -> f32 {
        self.listener_z
    }

    /// Set the listener facing angle (degrees, unit circle: 0 = +X east, 90 = +Y north/forward).
    pub fn set_listener_angle(&mut self, angle: f32) {
        self.listener_angle = angle;
        // Note: miniaudio uses direction vectors, not angles
        // We store the angle and use it in sound spatialization calculations
    }

    /// Get listener facing angle in degrees.
    pub fn listener_angle(&self) -> f32 {
        self.listener_angle
    }

    /// Get the sample rate of the audio engine.
    pub fn sample_rate(&self) -> u32 {
        if self.engine.is_null() {
            44100 // Default fallback
        } else {
            unsafe { ma_engine_get_sample_rate(self.engine) }
        }
    }
}

impl Drop for AudioEngine {
    fn drop(&mut self) {
        if self.hrtf_initialized {
            phonon_node::phonon_uninit();
        }
        if self.initialized && !self.engine.is_null() {
            unsafe {
                ma_engine_uninit_with_caching(self.engine);
                ma_engine_free(self.engine);
            }
        }
    }
}

// SAFETY: `AudioEngine` owns its `ma_engine` exclusively, and every use of the
// pointer goes through the `Mutex` that `SoundManager`, sounds and groups
// share, so at most one caller thread touches it at a time. miniaudio's own
// audio thread synchronises with callers internally (property setters are
// atomic, graph edits are lock-free by design), so the calling thread's
// identity does not matter.
unsafe impl Send for AudioEngine {}
