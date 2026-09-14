//! Offline time stretching (SOLA / WSOLA-lite).
//!
//! Produces a pitch-preserving, time-scaled copy of an interleaved f32 PCM
//! buffer. Works by overlap-adding Hann-windowed grains, with a small
//! cross-correlation search to keep grain boundaries phase-aligned.
//!
//! Good for voicepack sounds (pain, death) at stretch factors 0.5x .. 3.0x.
//! Fast and perfectly adequate for game SFX — not broadcast quality.

use std::f32::consts::PI;

/// Target grain size at 48kHz (~43ms). Scales linearly with sample rate.
const TARGET_GRAIN_MS: f32 = 43.0;
/// Overlap factor — hop = grain / 4 (75% overlap).
const HOP_DIVISOR: usize = 4;
/// WSOLA search radius as a fraction of hop size.
const SEARCH_FRACTION: f32 = 0.5;

/// Time-stretch an interleaved f32 PCM buffer.
///
/// `factor > 1.0` makes the output longer (slower); `factor < 1.0` shortens
/// (faster). `factor == 1.0` returns a copy.
///
/// Pitch is preserved to the extent that SOLA permits — small artifacts on
/// highly tonal material, fine on voice/noise.
pub fn ola_stretch(
    input: &[f32],
    channels: usize,
    sample_rate: u32,
    factor: f32,
) -> Vec<f32> {
    if input.is_empty() || channels == 0 || factor <= 0.05 {
        return Vec::new();
    }
    if (factor - 1.0).abs() < 1e-3 {
        return input.to_vec();
    }

    let input_frames = input.len() / channels;
    let output_frames = ((input_frames as f32) * factor).ceil() as usize;
    if output_frames == 0 {
        return Vec::new();
    }

    let grain = {
        let target = ((TARGET_GRAIN_MS / 1000.0) * sample_rate as f32) as usize;
        target.clamp(256, 4096).min(input_frames.max(256))
    };
    let hop_out = (grain / HOP_DIVISOR).max(1);
    let hop_in = ((hop_out as f32) / factor).round() as i64;
    let search = ((hop_out as f32 * SEARCH_FRACTION) as usize).min(hop_in.unsigned_abs() as usize);

    let window = hann_window(grain);

    let mut output = vec![0.0f32; output_frames * channels];
    // Per-frame window sum, for normalization.
    let mut norm = vec![0.0f32; output_frames];

    // Reference tail for correlation: the last `overlap_ref` output frames
    // from the previous grain — we want the next input grain to correlate with.
    let overlap_ref = grain / 2;

    let mut in_pos: i64 = 0;
    let mut out_pos: usize = 0;
    let mut first_grain = true;

    while out_pos + grain <= output_frames {
        // WSOLA: search for the best input offset that matches the output tail.
        let best_in = if first_grain {
            in_pos
        } else {
            find_best_offset(input, channels, in_pos, search, &output, out_pos, overlap_ref, input_frames)
        };

        // Overlap-add a Hann-windowed grain.
        for i in 0..grain {
            let src_frame = best_in + i as i64;
            if src_frame < 0 || (src_frame as usize) >= input_frames {
                continue;
            }
            let w = window[i];
            let out_frame = out_pos + i;
            for c in 0..channels {
                output[out_frame * channels + c] +=
                    input[(src_frame as usize) * channels + c] * w;
            }
            norm[out_frame] += w;
        }

        in_pos += hop_in;
        out_pos += hop_out;
        first_grain = false;

        // Bail if we've run off the end of the source.
        if in_pos + grain as i64 > input_frames as i64 + search as i64 {
            break;
        }
    }

    // Normalize by the summed window weight at each output frame.
    // A plain 75% Hann-OLA yields ~1.0 everywhere in the steady state; this
    // just keeps the fade-in / fade-out edges at unity too.
    for i in 0..output_frames {
        let n = norm[i];
        if n > 1e-4 {
            let inv = 1.0 / n;
            for c in 0..channels {
                output[i * channels + c] *= inv;
            }
        }
    }

    output
}

/// Hann window (raised cosine), `len` samples.
fn hann_window(len: usize) -> Vec<f32> {
    if len <= 1 {
        return vec![1.0; len];
    }
    (0..len)
        .map(|i| 0.5 - 0.5 * ((2.0 * PI * i as f32) / (len - 1) as f32).cos())
        .collect()
}

/// Find the input offset near `nominal` (within ±`search` frames) whose
/// first `overlap_ref` frames best correlate with `output[out_pos..out_pos+overlap_ref]`.
/// Returns the chosen offset (may be negative, meaning slightly before nominal).
fn find_best_offset(
    input: &[f32],
    channels: usize,
    nominal: i64,
    search: usize,
    output: &[f32],
    out_pos: usize,
    overlap_ref: usize,
    input_frames: usize,
) -> i64 {
    if search == 0 {
        return nominal;
    }
    let mut best = nominal;
    let mut best_score = f32::NEG_INFINITY;

    let lo = (nominal - search as i64).max(0);
    let hi = (nominal + search as i64).min(input_frames as i64 - overlap_ref as i64);

    // Correlate on the first channel only — cheap and usually sufficient.
    // We use normalized cross-correlation to avoid biasing toward louder segments.
    let ref_start = out_pos * channels;

    // Precompute output tail energy.
    let mut out_energy = 0.0f32;
    for i in 0..overlap_ref {
        let s = output[ref_start + i * channels];
        out_energy += s * s;
    }
    if out_energy < 1e-8 {
        return nominal;
    }

    for candidate in lo..=hi {
        let mut corr = 0.0f32;
        let mut in_energy = 0.0f32;
        let base = (candidate as usize) * channels;
        for i in 0..overlap_ref {
            let o = output[ref_start + i * channels];
            let s = input[base + i * channels];
            corr += o * s;
            in_energy += s * s;
        }
        let denom = (out_energy * in_energy).sqrt();
        let score = if denom > 1e-8 { corr / denom } else { f32::NEG_INFINITY };
        if score > best_score {
            best_score = score;
            best = candidate;
        }
    }

    best
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn identity_on_factor_1() {
        let input: Vec<f32> = (0..1024).map(|i| (i as f32 * 0.01).sin()).collect();
        let out = ola_stretch(&input, 1, 48000, 1.0);
        assert_eq!(out.len(), input.len());
    }

    #[test]
    fn stretch_doubles_length() {
        let input: Vec<f32> = (0..4096).map(|i| (i as f32 * 0.01).sin()).collect();
        let out = ola_stretch(&input, 1, 48000, 2.0);
        // Should be ~2x input length (±1 grain of slack).
        assert!(out.len() >= input.len() * 2 - 2048);
        assert!(out.len() <= input.len() * 2 + 2048);
    }

    #[test]
    fn empty_input() {
        let out = ola_stretch(&[], 1, 48000, 2.0);
        assert!(out.is_empty());
    }
}
