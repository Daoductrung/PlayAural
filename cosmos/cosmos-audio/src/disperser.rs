//! Phase disperser (cascaded allpass) node wrapper.

use miniaudio_sys::{ma_node, ma_node_graph, ma_result, ma_uint32, MA_SUCCESS};
use std::ptr;

use crate::error::AudioError;

#[repr(C)]
pub struct DisperserNodeOpaque {
    _private: [u8; 0],
}

#[repr(C)]
#[allow(non_snake_case)]
pub struct DisperserNodeConfig {
    _blob: [u8; 512],
}

extern "C" {
    fn ma_disperser_node_alloc() -> *mut DisperserNodeOpaque;
    fn ma_disperser_node_free(node: *mut DisperserNodeOpaque);
    fn ma_disperser_node_init(
        graph: *mut ma_node_graph,
        config: *const DisperserNodeConfig,
        alloc_callbacks: *const core::ffi::c_void,
        node: *mut DisperserNodeOpaque,
    ) -> ma_result;
    fn ma_disperser_node_uninit(
        node: *mut DisperserNodeOpaque,
        alloc_callbacks: *const core::ffi::c_void,
    );
    fn ma_disperser_node_config_init(channels: ma_uint32, sample_rate: ma_uint32) -> DisperserNodeConfig;

    fn ma_disperser_node_set_freq(node: *mut DisperserNodeOpaque, hz: f32);
    fn ma_disperser_node_set_q(node: *mut DisperserNodeOpaque, q: f32);
    fn ma_disperser_node_set_stages(node: *mut DisperserNodeOpaque, stages: i32);
}

pub struct DisperserNode {
    node: *mut DisperserNodeOpaque,
    initialized: bool,

    freq: f32,
    q: f32,
    stages: i32,
}

impl DisperserNode {
    pub fn new(graph: *mut ma_node_graph, sample_rate: u32) -> Result<Self, AudioError> {
        let node = unsafe { ma_disperser_node_alloc() };
        if node.is_null() {
            return Err(AudioError::AllocationFailed);
        }
        let cfg = unsafe { ma_disperser_node_config_init(2, sample_rate) };
        let r = unsafe { ma_disperser_node_init(graph, &cfg, ptr::null(), node) };
        if r != MA_SUCCESS {
            unsafe { ma_disperser_node_free(node) };
            return Err(AudioError::AllocationFailed);
        }
        Ok(Self {
            node,
            initialized: true,
            freq: 800.0,
            q: 0.707,
            stages: 8,
        })
    }

    pub fn as_ma_node(&self) -> *mut ma_node {
        self.node as *mut ma_node
    }

    pub fn set_freq(&mut self, hz: f32)   { self.freq = hz; unsafe { ma_disperser_node_set_freq(self.node, hz) }; }
    pub fn set_q(&mut self, q: f32)       { self.q = q; unsafe { ma_disperser_node_set_q(self.node, q) }; }
    pub fn set_stages(&mut self, s: i32)  { self.stages = s; unsafe { ma_disperser_node_set_stages(self.node, s) }; }

    pub fn freq(&self) -> f32   { self.freq }
    pub fn q(&self) -> f32      { self.q }
    pub fn stages(&self) -> i32 { self.stages }
}

impl Drop for DisperserNode {
    fn drop(&mut self) {
        if self.initialized && !self.node.is_null() {
            unsafe {
                ma_disperser_node_uninit(self.node, ptr::null());
                ma_disperser_node_free(self.node);
            }
        }
    }
}
