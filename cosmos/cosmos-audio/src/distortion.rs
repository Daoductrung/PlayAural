//! Waveshaping distortion / overdrive node wrapper.

use miniaudio_sys::{ma_node, ma_node_graph, ma_result, ma_uint32, MA_SUCCESS};
use std::ptr;

use crate::error::AudioError;

#[repr(C)]
pub struct DistortionNodeOpaque {
    _private: [u8; 0],
}

#[repr(C)]
#[allow(non_snake_case)]
pub struct DistortionNodeConfig {
    _blob: [u8; 512],
}

extern "C" {
    fn ma_distortion_node_alloc() -> *mut DistortionNodeOpaque;
    fn ma_distortion_node_free(node: *mut DistortionNodeOpaque);
    fn ma_distortion_node_init(
        graph: *mut ma_node_graph,
        config: *const DistortionNodeConfig,
        alloc_callbacks: *const core::ffi::c_void,
        node: *mut DistortionNodeOpaque,
    ) -> ma_result;
    fn ma_distortion_node_uninit(
        node: *mut DistortionNodeOpaque,
        alloc_callbacks: *const core::ffi::c_void,
    );
    fn ma_distortion_node_config_init(channels: ma_uint32, sample_rate: ma_uint32) -> DistortionNodeConfig;

    fn ma_distortion_node_set_drive(node: *mut DistortionNodeOpaque, drive: f32);
    fn ma_distortion_node_set_tone(node: *mut DistortionNodeOpaque, hz: f32);
    fn ma_distortion_node_set_wet(node: *mut DistortionNodeOpaque, wet: f32);
    fn ma_distortion_node_set_dry(node: *mut DistortionNodeOpaque, dry: f32);
}

pub struct DistortionNode {
    node: *mut DistortionNodeOpaque,
    initialized: bool,

    drive: f32,
    tone: f32,
    wet: f32,
    dry: f32,
}

impl DistortionNode {
    pub fn new(graph: *mut ma_node_graph, sample_rate: u32) -> Result<Self, AudioError> {
        let node = unsafe { ma_distortion_node_alloc() };
        if node.is_null() {
            return Err(AudioError::AllocationFailed);
        }
        let cfg = unsafe { ma_distortion_node_config_init(2, sample_rate) };
        let r = unsafe { ma_distortion_node_init(graph, &cfg, ptr::null(), node) };
        if r != MA_SUCCESS {
            unsafe { ma_distortion_node_free(node) };
            return Err(AudioError::AllocationFailed);
        }
        Ok(Self {
            node,
            initialized: true,
            drive: 4.0,
            tone: 8000.0,
            wet: 0.5,
            dry: 0.5,
        })
    }

    pub fn as_ma_node(&self) -> *mut ma_node {
        self.node as *mut ma_node
    }

    pub fn set_drive(&mut self, drive: f32) { self.drive = drive; unsafe { ma_distortion_node_set_drive(self.node, drive) }; }
    pub fn set_tone(&mut self, hz: f32)     { self.tone = hz;     unsafe { ma_distortion_node_set_tone(self.node, hz) }; }
    pub fn set_wet(&mut self, wet: f32)     { self.wet = wet;     unsafe { ma_distortion_node_set_wet(self.node, wet) }; }
    pub fn set_dry(&mut self, dry: f32)     { self.dry = dry;     unsafe { ma_distortion_node_set_dry(self.node, dry) }; }

    pub fn drive(&self) -> f32 { self.drive }
    pub fn tone(&self) -> f32  { self.tone }
    pub fn wet(&self) -> f32   { self.wet }
    pub fn dry(&self) -> f32   { self.dry }
}

impl Drop for DistortionNode {
    fn drop(&mut self) {
        if self.initialized && !self.node.is_null() {
            unsafe {
                ma_distortion_node_uninit(self.node, ptr::null());
                ma_distortion_node_free(self.node);
            }
        }
    }
}
