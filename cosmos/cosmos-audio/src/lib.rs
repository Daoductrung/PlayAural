//! Cosmos Audio - High-level 3D audio library with HRTF support.
//!
//! This crate provides a safe, high-level API for audio playback with 3D positioning.
//! It supports both basic pan/volume spatialization and HRTF (Head-Related Transfer Function)
//! processing via Steam Audio.
//!
//! # Example
//!
//! ```no_run
//! use cosmos_audio::{SoundManager, Sound};
//!
//! // Create a sound manager
//! let mut manager = SoundManager::new()?;
//!
//! // Create and load a sound
//! let sound = manager.create_sound();
//! {
//!     let mut sound = sound.lock().unwrap_or_else(|poisoned| poisoned.into_inner());
//!     sound.load("audio/footstep.ogg")?;
//!
//!     // Enable HRTF for immersive 3D audio
//!     sound.set_hrtf(true);
//!
//!     // Position the sound in 3D space
//!     sound.set_position(5.0, 10.0, 0.0);
//!
//!     // Play the sound
//!     sound.play()?;
//! }
//!
//! // Update listener position (e.g., in game loop)
//! manager.set_listener(0.0, 0.0, 0.0, 90.0); // x, y, z, angle
//! # Ok::<(), cosmos_audio::AudioError>(())
//! ```
//!
//! # Coordinate System
//!
//! - X: Left (-) / Right (+)
//! - Y: Backward (-) / Forward (+)
//! - Z: Down (-) / Up (+)
//!
//! Listener angle is in degrees: 0 = +X (east), 90 = +Y (north/forward)

mod decode;
mod delay;
mod disperser;
mod distortion;
mod engine;
mod eq;
mod error;
mod filter;
mod group;
mod manager;
mod phonon_node;
mod reverb;
mod sound;
mod stretcher;
mod sync;
mod tween;
mod vocoder;
mod volume;

pub use engine::AudioEngine;
pub use error::AudioError;
pub use group::{SoundGroup, SoundGroupRef};
pub use manager::{SoundManager, SoundRef};
pub use phonon_node::HrtfInterpolation;
pub use sound::{Sound, SpatialMode};
pub use tween::Easing;
pub use volume::{db_to_linear, linear_to_db, pan_db_to_linear, pan_linear_to_db};

/// Result type for audio operations.
pub type Result<T> = std::result::Result<T, AudioError>;
