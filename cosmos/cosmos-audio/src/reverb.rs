//! Convolution (impulse-response) reverb node wrapper.
//!
//! FFI bindings to `ma_convreverb.c`. The C side implements a uniformly-
//! partitioned FFT convolution, decodes impulse responses via miniaudio, and
//! manages a double-buffered filter swap. This module just owns the node and
//! re-exports the parameter setters + IR loading.

use miniaudio_sys::{ma_node, ma_node_graph, ma_result, ma_uint32, MA_SUCCESS};
use std::ffi::CString;
use std::ptr;

use crate::error::AudioError;

/// Opaque handle. The real struct size lives in the C side — only ever
/// manipulate through the `ma_convreverb_node_*` functions.
#[repr(C)]
pub struct ConvReverbNodeOpaque {
    _private: [u8; 0],
}

extern "C" {
    fn ma_convreverb_node_alloc() -> *mut ConvReverbNodeOpaque;
    fn ma_convreverb_node_free(node: *mut ConvReverbNodeOpaque);

    fn ma_convreverb_node_init(
        graph: *mut ma_node_graph,
        config: *const ConvReverbNodeConfig,
        alloc_callbacks: *const core::ffi::c_void,
        node: *mut ConvReverbNodeOpaque,
    ) -> ma_result;

    fn ma_convreverb_node_uninit(
        node: *mut ConvReverbNodeOpaque,
        alloc_callbacks: *const core::ffi::c_void,
    );

    fn ma_convreverb_node_config_init(channels: ma_uint32, sample_rate: ma_uint32) -> ConvReverbNodeConfig;

    fn ma_convreverb_node_set_wet(node: *mut ConvReverbNodeOpaque, v: f32);
    fn ma_convreverb_node_set_dry(node: *mut ConvReverbNodeOpaque, v: f32);
    fn ma_convreverb_node_set_predelay(node: *mut ConvReverbNodeOpaque, v: f32);
    fn ma_convreverb_node_set_ir_gain(node: *mut ConvReverbNodeOpaque, v: f32);
    fn ma_convreverb_node_set_width(node: *mut ConvReverbNodeOpaque, v: f32);
    fn ma_convreverb_node_set_lowcut(node: *mut ConvReverbNodeOpaque, v: f32);
    fn ma_convreverb_node_set_highcut(node: *mut ConvReverbNodeOpaque, v: f32);
    fn ma_convreverb_node_set_diffuse(node: *mut ConvReverbNodeOpaque, v: f32);
    fn ma_convreverb_node_set_decay(node: *mut ConvReverbNodeOpaque, v: f32);

    fn ma_convreverb_node_load_ir_file(node: *mut ConvReverbNodeOpaque, path: *const core::ffi::c_char) -> ma_result;
    fn ma_convreverb_node_load_default_ir(node: *mut ConvReverbNodeOpaque) -> ma_result;
    fn ma_convreverb_node_ir_frames(node: *mut ConvReverbNodeOpaque) -> ma_uint32;
}

// The C-side config struct, passed through untouched.
#[repr(C)]
#[allow(non_snake_case)]
pub struct ConvReverbNodeConfig {
    _blob: [u8; 512],
}

/// A convolution reverb node living inside an ma_node_graph. Defaults to a
/// synthetic decaying-noise IR; load a custom one with [`ConvReverbNode::load_ir`].
pub struct ReverbNode {
    node: *mut ConvReverbNodeOpaque,
    initialized: bool,

    // Cached parameter state so the Python side can read them back.
    wet: f32,
    dry: f32,
    predelay: f32,
    ir_gain: f32,
    width: f32,
    decay: f32,
    lowcut: f32,
    highcut: f32,
    diffuse: f32,
    ir_path: Option<String>,
}

impl ReverbNode {
    /// Create and initialize a convolution reverb node on the given graph.
    pub fn new(graph: *mut ma_node_graph, sample_rate: u32) -> Result<Self, AudioError> {
        let node = unsafe { ma_convreverb_node_alloc() };
        if node.is_null() {
            return Err(AudioError::AllocationFailed);
        }

        let cfg = unsafe { ma_convreverb_node_config_init(2, sample_rate) };
        let r = unsafe { ma_convreverb_node_init(graph, &cfg, ptr::null(), node) };
        if r != MA_SUCCESS {
            unsafe { ma_convreverb_node_free(node) };
            return Err(AudioError::AllocationFailed);
        }

        Ok(Self {
            node,
            initialized: true,
            wet: 0.33,
            dry: 1.0,
            predelay: 0.0,
            ir_gain: 1.0,
            width: 1.0,
            decay: 1.0,
            lowcut: 20.0,
            highcut: 18000.0,
            diffuse: 1.0,
            ir_path: None,
        })
    }

    /// Raw node pointer — for attaching inputs / downstream outputs.
    pub fn as_ma_node(&self) -> *mut ma_node {
        self.node as *mut ma_node
    }

    pub fn set_wet(&mut self, v: f32) {
        self.wet = v.clamp(0.0, 1.0);
        if self.initialized { unsafe { ma_convreverb_node_set_wet(self.node, self.wet) }; }
    }
    pub fn wet(&self) -> f32 { self.wet }

    pub fn set_dry(&mut self, v: f32) {
        self.dry = v.clamp(0.0, 1.0);
        if self.initialized { unsafe { ma_convreverb_node_set_dry(self.node, self.dry) }; }
    }
    pub fn dry(&self) -> f32 { self.dry }

    pub fn set_predelay(&mut self, v: f32) {
        self.predelay = v.clamp(0.0, 250.0);
        if self.initialized { unsafe { ma_convreverb_node_set_predelay(self.node, self.predelay) }; }
    }
    pub fn predelay(&self) -> f32 { self.predelay }

    pub fn set_ir_gain(&mut self, v: f32) {
        self.ir_gain = v.clamp(0.0, 4.0);
        if self.initialized { unsafe { ma_convreverb_node_set_ir_gain(self.node, self.ir_gain) }; }
    }
    pub fn ir_gain(&self) -> f32 { self.ir_gain }

    pub fn set_width(&mut self, v: f32) {
        self.width = v.clamp(0.0, 2.0);
        if self.initialized { unsafe { ma_convreverb_node_set_width(self.node, self.width) }; }
    }
    pub fn width(&self) -> f32 { self.width }

    pub fn set_lowcut(&mut self, v: f32) {
        self.lowcut = v.clamp(10.0, 20000.0);
        if self.initialized { unsafe { ma_convreverb_node_set_lowcut(self.node, self.lowcut) }; }
    }
    pub fn lowcut(&self) -> f32 { self.lowcut }

    pub fn set_highcut(&mut self, v: f32) {
        self.highcut = v.clamp(40.0, 20000.0);
        if self.initialized { unsafe { ma_convreverb_node_set_highcut(self.node, self.highcut) }; }
    }
    pub fn highcut(&self) -> f32 { self.highcut }

    /// 0 = wet follows the source's pan; 1 = mono send → diffuse tail that
    /// doesn't pan with the source.
    pub fn set_diffuse(&mut self, v: f32) {
        self.diffuse = v.clamp(0.0, 1.0);
        if self.initialized { unsafe { ma_convreverb_node_set_diffuse(self.node, self.diffuse) }; }
    }
    pub fn diffuse(&self) -> f32 { self.diffuse }

    /// Tail-shaping. 1.0 = use the IR unchanged; smaller shortens the tail.
    /// Rebuilds the partitioned filter (control-thread work).
    pub fn set_decay(&mut self, v: f32) {
        self.decay = v.clamp(0.05, 1.0);
        if self.initialized { unsafe { ma_convreverb_node_set_decay(self.node, self.decay) }; }
    }
    pub fn decay(&self) -> f32 { self.decay }

    /// Load a custom impulse response from any decodable audio file. Returns
    /// Ok on success; the prior IR is kept on failure.
    pub fn load_ir(&mut self, path: &str) -> Result<(), AudioError> {
        if !self.initialized {
            return Err(AudioError::AllocationFailed);
        }
        let c = CString::new(path).map_err(|_| AudioError::AllocationFailed)?;
        let r = unsafe { ma_convreverb_node_load_ir_file(self.node, c.as_ptr()) };
        if r != MA_SUCCESS {
            return Err(AudioError::AllocationFailed);
        }
        self.ir_path = Some(path.to_string());
        Ok(())
    }

    /// Restore the built-in synthetic IR.
    pub fn load_default_ir(&mut self) -> Result<(), AudioError> {
        if !self.initialized {
            return Err(AudioError::AllocationFailed);
        }
        let r = unsafe { ma_convreverb_node_load_default_ir(self.node) };
        if r != MA_SUCCESS {
            return Err(AudioError::AllocationFailed);
        }
        self.ir_path = None;
        Ok(())
    }

    /// Length of the loaded IR in frames.
    pub fn ir_frames(&self) -> u32 {
        if self.initialized { unsafe { ma_convreverb_node_ir_frames(self.node) } } else { 0 }
    }

    /// Path of the loaded custom IR, or None when using the default.
    pub fn ir_path(&self) -> Option<&str> {
        self.ir_path.as_deref()
    }
}

impl Drop for ReverbNode {
    fn drop(&mut self) {
        if self.initialized && !self.node.is_null() {
            unsafe {
                ma_convreverb_node_uninit(self.node, ptr::null());
                ma_convreverb_node_free(self.node);
            }
        }
    }
}
