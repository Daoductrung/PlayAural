//! Raw FFI bindings to miniaudio.
//!
//! This crate provides low-level bindings to the miniaudio library.
//! For a safe, high-level API, use the `cosmos-audio` crate instead.

#![allow(non_upper_case_globals)]
#![allow(non_camel_case_types)]
#![allow(non_snake_case)]
#![allow(dead_code)]
#![allow(clippy::all)]

// Committed bindgen output; regenerate with `--features regen-bindings`.
include!("bindings.rs");

// Re-export common bool constants — the enum-based MA_SUCCESS / MA_ERROR now
// come straight from bindgen (prepend_enum_name disabled), so no manual redef.
pub const MA_TRUE: ma_bool32 = 1;
pub const MA_FALSE: ma_bool32 = 0;

// Sound flags
pub const MA_SOUND_FLAG_STREAM: ma_uint32 = 0x00000001;
pub const MA_SOUND_FLAG_DECODE: ma_uint32 = 0x00000002;
pub const MA_SOUND_FLAG_ASYNC: ma_uint32 = 0x00000004;
pub const MA_SOUND_FLAG_WAIT_INIT: ma_uint32 = 0x00000008;
pub const MA_SOUND_FLAG_NO_DEFAULT_ATTACHMENT: ma_uint32 = 0x00000010;
pub const MA_SOUND_FLAG_NO_PITCH: ma_uint32 = 0x00000020;
pub const MA_SOUND_FLAG_NO_SPATIALIZATION: ma_uint32 = 0x00000040;

// Helper functions defined in miniaudio_impl.c
extern "C" {
    pub fn ma_engine_alloc() -> *mut ma_engine;
    pub fn ma_engine_free(engine: *mut ma_engine);
    pub fn ma_sound_alloc() -> *mut ma_sound;
    pub fn ma_sound_free(sound: *mut ma_sound);
    pub fn ma_engine_init_with_caching(pEngine: *mut ma_engine) -> ma_result;
    pub fn ma_engine_uninit_with_caching(pEngine: *mut ma_engine);
    pub fn ma_sound_get_node_ptr(pSound: *mut ma_sound) -> *mut ma_node;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_constants() {
        assert_eq!(MA_SUCCESS, 0);
        assert_eq!(MA_TRUE, 1);
        assert_eq!(MA_FALSE, 0);
    }
}
