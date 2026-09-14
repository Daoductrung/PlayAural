//! Decode an audio file to an interleaved f32 PCM buffer in memory.

use miniaudio_sys::{
    ma_data_source_get_length_in_pcm_frames, ma_decoder, ma_decoder_config_init,
    ma_decoder_get_data_format, ma_decoder_init_file, ma_decoder_read_pcm_frames,
    ma_decoder_uninit, ma_format, ma_format_f32, ma_uint32, ma_uint64, MA_SUCCESS,
};
use std::ffi::CString;
use std::mem::MaybeUninit;

use crate::error::AudioError;

/// Decoded audio: interleaved f32 samples plus format metadata.
pub struct Decoded {
    pub samples: Vec<f32>,
    pub channels: u32,
    pub sample_rate: u32,
}

// miniaudio's ma_decoder struct is opaque in our bindings (bindgen sees the
// union fields). Allocate enough raw storage to hold it — a generous 4KB is
// well over the ~2KB the struct actually uses. Alignment covered by the
// platform's max_align default via `#[repr(align(16))]`.
#[repr(C, align(16))]
struct DecoderStorage([u8; 4096]);

/// Decode an audio file completely into memory. Forces output to f32 and
/// resamples to `sample_rate`. Returns the interleaved PCM plus metadata.
pub fn decode_file(path: &str, sample_rate: u32) -> Result<Decoded, AudioError> {
    let c_path = CString::new(path).map_err(|_| AudioError::LoadFailed(path.to_string()))?;

    let config = unsafe { ma_decoder_config_init(ma_format_f32, 0, sample_rate) };

    // Opaque ma_decoder — we don't reach into its fields; only use API funcs.
    let mut storage = MaybeUninit::<DecoderStorage>::zeroed();
    let decoder_ptr = storage.as_mut_ptr() as *mut ma_decoder;

    let result = unsafe { ma_decoder_init_file(c_path.as_ptr(), &config, decoder_ptr) };
    if result != MA_SUCCESS {
        return Err(AudioError::LoadFailed(path.to_string()));
    }

    // Query output channels and sample rate via the public API.
    let mut out_format: ma_format = 0;
    let mut out_channels: ma_uint32 = 0;
    let mut out_sample_rate: ma_uint32 = 0;
    let r = unsafe {
        ma_decoder_get_data_format(
            decoder_ptr,
            &mut out_format,
            &mut out_channels,
            &mut out_sample_rate,
            std::ptr::null_mut(),
            0,
        )
    };
    if r != MA_SUCCESS || out_channels == 0 {
        unsafe { ma_decoder_uninit(decoder_ptr) };
        return Err(AudioError::LoadFailed(path.to_string()));
    }

    // Length in frames is best-effort — some formats don't know it up front.
    let mut length_frames: ma_uint64 = 0;
    let _ = unsafe {
        ma_data_source_get_length_in_pcm_frames(
            decoder_ptr as *mut _,
            &mut length_frames,
        )
    };
    let capacity = if length_frames > 0 {
        (length_frames as usize) * (out_channels as usize)
    } else {
        0
    };

    let mut samples: Vec<f32> = Vec::with_capacity(capacity);
    let chunk_frames: u64 = 4096;
    let mut chunk = vec![0.0f32; (chunk_frames as usize) * (out_channels as usize)];

    loop {
        let mut frames_read: ma_uint64 = 0;
        let r = unsafe {
            ma_decoder_read_pcm_frames(
                decoder_ptr,
                chunk.as_mut_ptr() as *mut std::ffi::c_void,
                chunk_frames,
                &mut frames_read,
            )
        };
        if frames_read > 0 {
            let n = (frames_read as usize) * (out_channels as usize);
            samples.extend_from_slice(&chunk[..n]);
        }
        if r != MA_SUCCESS || frames_read == 0 {
            break;
        }
    }

    unsafe { ma_decoder_uninit(decoder_ptr) };

    Ok(Decoded {
        samples,
        channels: out_channels,
        sample_rate: out_sample_rate,
    })
}
