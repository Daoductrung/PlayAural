//! 3-band EQ node wrapper (low shelf + mid peak + high shelf).

use miniaudio_sys::{ma_node, ma_node_graph, ma_result, ma_uint32, MA_SUCCESS};
use std::ptr;

use crate::error::AudioError;

#[repr(C)]
pub struct EqNodeOpaque {
    _private: [u8; 0],
}

#[repr(C)]
#[allow(non_snake_case)]
pub struct EqNodeConfig {
    _blob: [u8; 512],
}

extern "C" {
    fn ma_eq_node_alloc() -> *mut EqNodeOpaque;
    fn ma_eq_node_free(node: *mut EqNodeOpaque);
    fn ma_eq_node_init(
        graph: *mut ma_node_graph,
        config: *const EqNodeConfig,
        alloc_callbacks: *const core::ffi::c_void,
        node: *mut EqNodeOpaque,
    ) -> ma_result;
    fn ma_eq_node_uninit(
        node: *mut EqNodeOpaque,
        alloc_callbacks: *const core::ffi::c_void,
    );
    fn ma_eq_node_config_init(channels: ma_uint32, sample_rate: ma_uint32) -> EqNodeConfig;

    fn ma_eq_node_set_low_gain(node: *mut EqNodeOpaque, db: f32);
    fn ma_eq_node_set_mid_gain(node: *mut EqNodeOpaque, db: f32);
    fn ma_eq_node_set_high_gain(node: *mut EqNodeOpaque, db: f32);
    fn ma_eq_node_set_low_freq(node: *mut EqNodeOpaque, hz: f32);
    fn ma_eq_node_set_mid_freq(node: *mut EqNodeOpaque, hz: f32);
    fn ma_eq_node_set_high_freq(node: *mut EqNodeOpaque, hz: f32);
    fn ma_eq_node_set_mid_q(node: *mut EqNodeOpaque, q: f32);
}

pub struct EqNode {
    node: *mut EqNodeOpaque,
    initialized: bool,

    low_gain: f32,
    mid_gain: f32,
    high_gain: f32,
    low_freq: f32,
    mid_freq: f32,
    high_freq: f32,
    mid_q: f32,
}

impl EqNode {
    pub fn new(graph: *mut ma_node_graph, sample_rate: u32) -> Result<Self, AudioError> {
        let node = unsafe { ma_eq_node_alloc() };
        if node.is_null() {
            return Err(AudioError::AllocationFailed);
        }
        let cfg = unsafe { ma_eq_node_config_init(2, sample_rate) };
        let r = unsafe { ma_eq_node_init(graph, &cfg, ptr::null(), node) };
        if r != MA_SUCCESS {
            unsafe { ma_eq_node_free(node) };
            return Err(AudioError::AllocationFailed);
        }
        Ok(Self {
            node,
            initialized: true,
            low_gain: 0.0,
            mid_gain: 0.0,
            high_gain: 0.0,
            low_freq: 200.0,
            mid_freq: 2000.0,
            high_freq: 5000.0,
            mid_q: 1.0,
        })
    }

    pub fn as_ma_node(&self) -> *mut ma_node {
        self.node as *mut ma_node
    }

    pub fn set_low_gain(&mut self, db: f32)  { self.low_gain = db; unsafe { ma_eq_node_set_low_gain(self.node, db) }; }
    pub fn set_mid_gain(&mut self, db: f32)  { self.mid_gain = db; unsafe { ma_eq_node_set_mid_gain(self.node, db) }; }
    pub fn set_high_gain(&mut self, db: f32) { self.high_gain = db; unsafe { ma_eq_node_set_high_gain(self.node, db) }; }
    pub fn set_low_freq(&mut self, hz: f32)  { self.low_freq = hz; unsafe { ma_eq_node_set_low_freq(self.node, hz) }; }
    pub fn set_mid_freq(&mut self, hz: f32)  { self.mid_freq = hz; unsafe { ma_eq_node_set_mid_freq(self.node, hz) }; }
    pub fn set_high_freq(&mut self, hz: f32) { self.high_freq = hz; unsafe { ma_eq_node_set_high_freq(self.node, hz) }; }
    pub fn set_mid_q(&mut self, q: f32)      { self.mid_q = q; unsafe { ma_eq_node_set_mid_q(self.node, q) }; }

    pub fn low_gain(&self) -> f32  { self.low_gain }
    pub fn mid_gain(&self) -> f32  { self.mid_gain }
    pub fn high_gain(&self) -> f32 { self.high_gain }
    pub fn low_freq(&self) -> f32  { self.low_freq }
    pub fn mid_freq(&self) -> f32  { self.mid_freq }
    pub fn high_freq(&self) -> f32 { self.high_freq }
    pub fn mid_q(&self) -> f32     { self.mid_q }
}

impl Drop for EqNode {
    fn drop(&mut self) {
        if self.initialized && !self.node.is_null() {
            unsafe {
                ma_eq_node_uninit(self.node, ptr::null());
                ma_eq_node_free(self.node);
            }
        }
    }
}
