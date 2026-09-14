//! Stereo feedback delay / echo node wrapper.

use miniaudio_sys::{ma_node, ma_node_graph, ma_result, ma_uint32, MA_SUCCESS};
use std::ptr;

use crate::error::AudioError;

#[repr(C)]
pub struct DelayNodeOpaque {
    _private: [u8; 0],
}

#[repr(C)]
#[allow(non_snake_case)]
pub struct DelayNodeConfig {
    _blob: [u8; 512],
}

extern "C" {
    fn ma_delay_fx_alloc() -> *mut DelayNodeOpaque;
    fn ma_delay_fx_free(node: *mut DelayNodeOpaque);
    fn ma_delay_fx_init(
        graph: *mut ma_node_graph,
        config: *const DelayNodeConfig,
        alloc_callbacks: *const core::ffi::c_void,
        node: *mut DelayNodeOpaque,
    ) -> ma_result;
    fn ma_delay_fx_uninit(
        node: *mut DelayNodeOpaque,
        alloc_callbacks: *const core::ffi::c_void,
    );
    fn ma_delay_fx_config_init(channels: ma_uint32, sample_rate: ma_uint32) -> DelayNodeConfig;

    fn ma_delay_fx_set_delay_ms(node: *mut DelayNodeOpaque, ms: f32);
    fn ma_delay_fx_set_feedback(node: *mut DelayNodeOpaque, fb: f32);
    fn ma_delay_fx_set_wet(node: *mut DelayNodeOpaque, wet: f32);
    fn ma_delay_fx_set_dry(node: *mut DelayNodeOpaque, dry: f32);
}

pub struct DelayNode {
    node: *mut DelayNodeOpaque,
    initialized: bool,

    delay_ms: f32,
    feedback: f32,
    wet: f32,
    dry: f32,
}

impl DelayNode {
    pub fn new(graph: *mut ma_node_graph, sample_rate: u32) -> Result<Self, AudioError> {
        let node = unsafe { ma_delay_fx_alloc() };
        if node.is_null() {
            return Err(AudioError::AllocationFailed);
        }
        let cfg = unsafe { ma_delay_fx_config_init(2, sample_rate) };
        let r = unsafe { ma_delay_fx_init(graph, &cfg, ptr::null(), node) };
        if r != MA_SUCCESS {
            unsafe { ma_delay_fx_free(node) };
            return Err(AudioError::AllocationFailed);
        }
        Ok(Self {
            node,
            initialized: true,
            delay_ms: 300.0,
            feedback: 0.35,
            wet: 0.35,
            dry: 1.0,
        })
    }

    pub fn as_ma_node(&self) -> *mut ma_node {
        self.node as *mut ma_node
    }

    pub fn set_delay_ms(&mut self, ms: f32) { self.delay_ms = ms; unsafe { ma_delay_fx_set_delay_ms(self.node, ms) }; }
    pub fn set_feedback(&mut self, fb: f32) { self.feedback = fb; unsafe { ma_delay_fx_set_feedback(self.node, fb) }; }
    pub fn set_wet(&mut self, wet: f32)     { self.wet = wet;     unsafe { ma_delay_fx_set_wet(self.node, wet) }; }
    pub fn set_dry(&mut self, dry: f32)     { self.dry = dry;     unsafe { ma_delay_fx_set_dry(self.node, dry) }; }

    pub fn delay_ms(&self) -> f32 { self.delay_ms }
    pub fn feedback(&self) -> f32 { self.feedback }
    pub fn wet(&self) -> f32      { self.wet }
    pub fn dry(&self) -> f32      { self.dry }
}

impl Drop for DelayNode {
    fn drop(&mut self) {
        if self.initialized && !self.node.is_null() {
            unsafe {
                ma_delay_fx_uninit(self.node, ptr::null());
                ma_delay_fx_free(self.node);
            }
        }
    }
}
