//! Shared tween primitives for pitch automation on sounds and groups.

use std::time::{Duration, Instant};

/// Easing curves for value automation (e.g. pitch tweens).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Easing {
    Linear,
    EaseIn,
    EaseOut,
    EaseInOut,
}

impl Easing {
    /// Apply the easing curve to a normalized progress value in [0, 1].
    pub fn apply(self, t: f32) -> f32 {
        let t = t.clamp(0.0, 1.0);
        match self {
            Easing::Linear => t,
            Easing::EaseIn => t * t,
            Easing::EaseOut => 1.0 - (1.0 - t) * (1.0 - t),
            Easing::EaseInOut => {
                if t < 0.5 {
                    2.0 * t * t
                } else {
                    let u = -2.0 * t + 2.0;
                    1.0 - (u * u) / 2.0
                }
            }
        }
    }
}

/// Linear/eased interpolation of a scalar value over wall-clock time.
pub(crate) struct PitchTween {
    pub start_pitch: f32,
    pub target_pitch: f32,
    pub started: Instant,
    pub duration: Duration,
    pub easing: Easing,
}

impl PitchTween {
    /// Returns (current_value, finished).
    pub fn sample(&self) -> (f32, bool) {
        if self.duration.is_zero() {
            return (self.target_pitch, true);
        }
        let elapsed = self.started.elapsed();
        if elapsed >= self.duration {
            return (self.target_pitch, true);
        }
        let t = elapsed.as_secs_f32() / self.duration.as_secs_f32();
        let eased = self.easing.apply(t);
        let value = self.start_pitch + (self.target_pitch - self.start_pitch) * eased;
        (value, false)
    }
}
