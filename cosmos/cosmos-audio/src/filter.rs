//! Multimode biquad filter node wrapper (lowpass / highpass / bandpass /
//! notch / peak / low shelf / high shelf / allpass).

use miniaudio_sys::{ma_node, ma_node_graph, ma_result, ma_uint32, MA_SUCCESS};
use std::ptr;

use crate::error::AudioError;

#[repr(C)]
pub struct FilterNodeOpaque {
    _private: [u8; 0],
}

#[repr(C)]
#[allow(non_snake_case)]
pub struct FilterNodeConfig {
    _blob: [u8; 512],
}

extern "C" {
    fn ma_filter_node_alloc() -> *mut FilterNodeOpaque;
    fn ma_filter_node_free(node: *mut FilterNodeOpaque);
    fn ma_filter_node_init(
        graph: *mut ma_node_graph,
        config: *const FilterNodeConfig,
        alloc_callbacks: *const core::ffi::c_void,
        node: *mut FilterNodeOpaque,
    ) -> ma_result;
    fn ma_filter_node_uninit(
        node: *mut FilterNodeOpaque,
        alloc_callbacks: *const core::ffi::c_void,
    );
    fn ma_filter_node_config_init(channels: ma_uint32, sample_rate: ma_uint32) -> FilterNodeConfig;

    fn ma_filter_node_set_mode(node: *mut FilterNodeOpaque, mode: core::ffi::c_int);
    fn ma_filter_node_set_freq(node: *mut FilterNodeOpaque, hz: f32);
    fn ma_filter_node_set_q(node: *mut FilterNodeOpaque, q: f32);
    fn ma_filter_node_set_gain(node: *mut FilterNodeOpaque, db: f32);
}

pub struct FilterNode {
    node: *mut FilterNodeOpaque,
    initialized: bool,

    mode: i32,
    freq: f32,
    q: f32,
    gain: f32,
}

impl FilterNode {
    pub fn new(graph: *mut ma_node_graph, sample_rate: u32) -> Result<Self, AudioError> {
        let node = unsafe { ma_filter_node_alloc() };
        if node.is_null() {
            return Err(AudioError::AllocationFailed);
        }
        let cfg = unsafe { ma_filter_node_config_init(2, sample_rate) };
        let r = unsafe { ma_filter_node_init(graph, &cfg, ptr::null(), node) };
        if r != MA_SUCCESS {
            unsafe { ma_filter_node_free(node) };
            return Err(AudioError::AllocationFailed);
        }
        Ok(Self {
            node,
            initialized: true,
            mode: 0,
            freq: 1000.0,
            q: 0.707,
            gain: 0.0,
        })
    }

    pub fn as_ma_node(&self) -> *mut ma_node {
        self.node as *mut ma_node
    }

    pub fn set_mode(&mut self, mode: i32) { self.mode = mode; unsafe { ma_filter_node_set_mode(self.node, mode as core::ffi::c_int) }; }
    pub fn set_freq(&mut self, hz: f32)   { self.freq = hz;   unsafe { ma_filter_node_set_freq(self.node, hz) }; }
    pub fn set_q(&mut self, q: f32)       { self.q = q;       unsafe { ma_filter_node_set_q(self.node, q) }; }
    pub fn set_gain(&mut self, db: f32)   { self.gain = db;   unsafe { ma_filter_node_set_gain(self.node, db) }; }

    pub fn mode(&self) -> i32 { self.mode }
    pub fn freq(&self) -> f32 { self.freq }
    pub fn q(&self) -> f32    { self.q }
    pub fn gain(&self) -> f32 { self.gain }
}

impl Drop for FilterNode {
    fn drop(&mut self) {
        if self.initialized && !self.node.is_null() {
            unsafe {
                ma_filter_node_uninit(self.node, ptr::null());
                ma_filter_node_free(self.node);
            }
        }
    }
}
