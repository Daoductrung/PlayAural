//! Single-input channel vocoder node wrapper.

use miniaudio_sys::{ma_node, ma_node_graph, ma_result, ma_uint32, MA_SUCCESS};
use std::ptr;

use crate::error::AudioError;

#[repr(C)]
pub struct VocoderNodeOpaque {
    _private: [u8; 0],
}

#[repr(C)]
#[allow(non_snake_case)]
pub struct VocoderNodeConfig {
    _blob: [u8; 512],
}

extern "C" {
    fn ma_vocoder_node_alloc() -> *mut VocoderNodeOpaque;
    fn ma_vocoder_node_free(node: *mut VocoderNodeOpaque);
    fn ma_vocoder_node_init(
        graph: *mut ma_node_graph,
        config: *const VocoderNodeConfig,
        alloc_callbacks: *const core::ffi::c_void,
        node: *mut VocoderNodeOpaque,
    ) -> ma_result;
    fn ma_vocoder_node_uninit(
        node: *mut VocoderNodeOpaque,
        alloc_callbacks: *const core::ffi::c_void,
    );
    fn ma_vocoder_node_config_init(channels: ma_uint32, sample_rate: ma_uint32) -> VocoderNodeConfig;

    fn ma_vocoder_node_set_bands(node: *mut VocoderNodeOpaque, bands: core::ffi::c_int);
    fn ma_vocoder_node_set_carrier(node: *mut VocoderNodeOpaque, carrier: core::ffi::c_int);
    fn ma_vocoder_node_set_carrier_freq(node: *mut VocoderNodeOpaque, hz: f32);
    fn ma_vocoder_node_set_attack(node: *mut VocoderNodeOpaque, ms: f32);
    fn ma_vocoder_node_set_release(node: *mut VocoderNodeOpaque, ms: f32);
    fn ma_vocoder_node_set_wet(node: *mut VocoderNodeOpaque, wet: f32);
    fn ma_vocoder_node_set_dry(node: *mut VocoderNodeOpaque, dry: f32);
    fn ma_vocoder_node_set_rand(node: *mut VocoderNodeOpaque, on: core::ffi::c_int);
    fn ma_vocoder_node_set_rand_rate(node: *mut VocoderNodeOpaque, hz: f32);
    fn ma_vocoder_node_set_rand_depth(node: *mut VocoderNodeOpaque, octaves: f32);
    fn ma_vocoder_node_set_formant(node: *mut VocoderNodeOpaque, factor: f32);
    fn ma_vocoder_node_set_spread(node: *mut VocoderNodeOpaque, spread: f32);
    fn ma_vocoder_node_set_sibilance(node: *mut VocoderNodeOpaque, amt: f32);
}

pub struct VocoderNode {
    node: *mut VocoderNodeOpaque,
    initialized: bool,

    bands: i32,
    carrier: i32,
    carrier_freq: f32,
    attack: f32,
    release: f32,
    wet: f32,
    dry: f32,
    rand_on: bool,
    rand_rate: f32,
    rand_depth: f32,
    formant: f32,
    spread: f32,
    sibilance: f32,
}

impl VocoderNode {
    pub fn new(graph: *mut ma_node_graph, sample_rate: u32) -> Result<Self, AudioError> {
        let node = unsafe { ma_vocoder_node_alloc() };
        if node.is_null() {
            return Err(AudioError::AllocationFailed);
        }
        let cfg = unsafe { ma_vocoder_node_config_init(2, sample_rate) };
        let r = unsafe { ma_vocoder_node_init(graph, &cfg, ptr::null(), node) };
        if r != MA_SUCCESS {
            unsafe { ma_vocoder_node_free(node) };
            return Err(AudioError::AllocationFailed);
        }
        Ok(Self {
            node,
            initialized: true,
            bands: 16,
            carrier: 0,
            carrier_freq: 110.0,
            attack: 5.0,
            release: 60.0,
            wet: 1.0,
            dry: 0.0,
            rand_on: false,
            rand_rate: 6.0,
            rand_depth: 1.0,
            formant: 1.0,
            spread: 0.0,
            sibilance: 0.0,
        })
    }

    pub fn as_ma_node(&self) -> *mut ma_node {
        self.node as *mut ma_node
    }

    pub fn set_bands(&mut self, bands: i32)      { self.bands = bands; unsafe { ma_vocoder_node_set_bands(self.node, bands as core::ffi::c_int) }; }
    pub fn set_carrier(&mut self, carrier: i32)  { self.carrier = carrier; unsafe { ma_vocoder_node_set_carrier(self.node, carrier as core::ffi::c_int) }; }
    pub fn set_carrier_freq(&mut self, hz: f32)  { self.carrier_freq = hz; unsafe { ma_vocoder_node_set_carrier_freq(self.node, hz) }; }
    pub fn set_attack(&mut self, ms: f32)        { self.attack = ms; unsafe { ma_vocoder_node_set_attack(self.node, ms) }; }
    pub fn set_release(&mut self, ms: f32)       { self.release = ms; unsafe { ma_vocoder_node_set_release(self.node, ms) }; }
    pub fn set_wet(&mut self, wet: f32)          { self.wet = wet; unsafe { ma_vocoder_node_set_wet(self.node, wet) }; }
    pub fn set_dry(&mut self, dry: f32)          { self.dry = dry; unsafe { ma_vocoder_node_set_dry(self.node, dry) }; }

    pub fn set_rand(&mut self, on: bool)        { self.rand_on = on; unsafe { ma_vocoder_node_set_rand(self.node, if on { 1 } else { 0 }) }; }
    pub fn set_rand_rate(&mut self, hz: f32)    { self.rand_rate = hz; unsafe { ma_vocoder_node_set_rand_rate(self.node, hz) }; }
    pub fn set_rand_depth(&mut self, oct: f32)  { self.rand_depth = oct; unsafe { ma_vocoder_node_set_rand_depth(self.node, oct) }; }
    pub fn set_formant(&mut self, factor: f32)  { self.formant = factor; unsafe { ma_vocoder_node_set_formant(self.node, factor) }; }
    pub fn set_spread(&mut self, spread: f32)   { self.spread = spread; unsafe { ma_vocoder_node_set_spread(self.node, spread) }; }
    pub fn set_sibilance(&mut self, amt: f32)   { self.sibilance = amt; unsafe { ma_vocoder_node_set_sibilance(self.node, amt) }; }

    pub fn bands(&self) -> i32        { self.bands }
    pub fn carrier(&self) -> i32      { self.carrier }
    pub fn carrier_freq(&self) -> f32 { self.carrier_freq }
    pub fn attack(&self) -> f32       { self.attack }
    pub fn release(&self) -> f32      { self.release }
    pub fn wet(&self) -> f32          { self.wet }
    pub fn dry(&self) -> f32          { self.dry }
    pub fn rand_on(&self) -> bool     { self.rand_on }
    pub fn rand_rate(&self) -> f32    { self.rand_rate }
    pub fn rand_depth(&self) -> f32   { self.rand_depth }
    pub fn formant(&self) -> f32      { self.formant }
    pub fn spread(&self) -> f32       { self.spread }
    pub fn sibilance(&self) -> f32    { self.sibilance }
}

impl Drop for VocoderNode {
    fn drop(&mut self) {
        if self.initialized && !self.node.is_null() {
            unsafe {
                ma_vocoder_node_uninit(self.node, ptr::null());
                ma_vocoder_node_free(self.node);
            }
        }
    }
}
