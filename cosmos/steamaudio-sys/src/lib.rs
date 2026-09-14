//! Raw FFI bindings to Steam Audio (Phonon).
//!
//! This crate provides low-level bindings to the Steam Audio library.
//! For a safe, high-level API, use the `cosmos-audio` crate instead.

#![allow(non_upper_case_globals)]
#![allow(non_camel_case_types)]
#![allow(non_snake_case)]
#![allow(dead_code)]
#![allow(clippy::all)]

// Committed bindgen output; regenerate with `--features regen-bindings`.
include!("bindings.rs");

// Re-export common constants for convenience
pub const IPL_STATUS_SUCCESS: IPLerror = 0;
pub const IPL_STATUS_FAILURE: IPLerror = 1;
pub const IPL_STATUS_OUTOFMEMORY: IPLerror = 2;
pub const IPL_STATUS_INITIALIZATION: IPLerror = 3;

pub const IPL_HRTFTYPE_DEFAULT: IPLHRTFType = 0;
pub const IPL_HRTFTYPE_SOFA: IPLHRTFType = 1;

pub const IPL_HRTFINTERPOLATION_NEAREST: IPLHRTFInterpolation = 0;
pub const IPL_HRTFINTERPOLATION_BILINEAR: IPLHRTFInterpolation = 1;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_constants() {
        assert_eq!(IPL_STATUS_SUCCESS, 0);
    }
}
