//! Error types for the audio library.

use thiserror::Error;

/// Errors that can occur during audio operations.
#[derive(Error, Debug)]
pub enum AudioError {
    /// Failed to initialize the audio engine.
    #[error("Failed to initialize audio engine")]
    EngineInitFailed,

    /// Failed to allocate memory for an audio resource.
    #[error("Failed to allocate audio resource")]
    AllocationFailed,

    /// Failed to load an audio file.
    #[error("Failed to load audio file: {0}")]
    LoadFailed(String),

    /// Failed to start audio playback.
    #[error("Failed to start audio playback")]
    PlaybackFailed,

    /// The sound is not loaded.
    #[error("Sound not loaded")]
    NotLoaded,

    /// Failed to initialize Steam Audio.
    #[error("Failed to initialize Steam Audio")]
    PhononInitFailed,

    /// Failed to create binaural effect.
    #[error("Failed to create binaural effect")]
    BinauralEffectFailed,

    /// A miniaudio operation failed.
    #[error("Miniaudio error: {0}")]
    MiniaudioError(i32),

    /// A Steam Audio operation failed.
    #[error("Steam Audio error: {0}")]
    SteamAudioError(i32),
}
