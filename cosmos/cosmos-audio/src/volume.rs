//! Volume and pan conversion utilities for audio processing.
//!
//! Provides NVGT-compatible dB/linear conversions.

/// Convert linear volume to dB (miniaudio compatible).
/// Returns -100 dB for zero or negative input.
pub fn linear_to_db(linear: f32) -> f32 {
    if linear <= 0.0 {
        -100.0
    } else {
        20.0 * linear.log10()
    }
}

/// Convert dB to linear volume (miniaudio compatible).
pub fn db_to_linear(db: f32) -> f32 {
    10.0_f32.powf(db / 20.0)
}

/// Convert a dB pan value to linear (-1.0 to 1.0).
/// NVGT-style pan conversion.
pub fn pan_db_to_linear(db: f32) -> f32 {
    let db = db.clamp(-100.0, 100.0);
    let l = db_to_linear(-db.abs());
    if db > 0.0 {
        1.0 - l
    } else {
        -1.0 + l
    }
}

/// Convert a linear pan value (-1.0 to 1.0) to dB.
/// NVGT-style pan conversion.
pub fn pan_linear_to_db(linear: f32) -> f32 {
    let linear = linear.clamp(-1.0, 1.0);
    let db = linear_to_db(if linear > 0.0 {
        1.0 - linear
    } else {
        linear + 1.0
    });
    if linear > 0.0 {
        -db
    } else {
        db
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_linear_to_db() {
        assert_eq!(linear_to_db(1.0), 0.0);
        assert!((linear_to_db(0.5) - (-6.02)).abs() < 0.1);
        assert_eq!(linear_to_db(0.0), -100.0);
    }

    #[test]
    fn test_db_to_linear() {
        assert!((db_to_linear(0.0) - 1.0).abs() < 0.001);
        assert!((db_to_linear(-6.0) - 0.501).abs() < 0.01);
    }
}
