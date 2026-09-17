//! Sound manager for creating and managing audio playback.
//!
//! Replaces the global audio engine pattern with explicit ownership. Every
//! object handed out is `Send`, so sounds may be controlled from any thread
//! (a fade running on a worker thread, a GC finaliser on another).

use std::sync::{Arc, Mutex, Weak};

use crate::engine::AudioEngine;
use crate::error::AudioError;
use crate::group::{SoundGroup, SoundGroupRef};
use crate::sound::Sound;
use crate::sync::lock;

/// Sound wrapped in a shared, lockable reference for tracking by SoundManager.
pub type SoundRef = Arc<Mutex<Sound>>;

/// Manages the audio engine and sound creation.
///
/// Users should create a `SoundManager` instance and use it to create sounds.
///
/// # Example
///
/// ```no_run
/// use cosmos_audio::SoundManager;
///
/// let mut manager = SoundManager::new()?;
/// let sound = manager.create_sound();
/// sound.lock().unwrap().load("music.ogg")?;
/// sound.lock().unwrap().play()?;
/// # Ok::<(), cosmos_audio::AudioError>(())
/// ```
pub struct SoundManager {
    engine: Arc<Mutex<AudioEngine>>,
    /// Weak references to all sounds for updating when listener changes
    sounds: Vec<Weak<Mutex<Sound>>>,
    /// Weak references to all groups for ticking pitch tweens.
    groups: Vec<Weak<Mutex<SoundGroup>>>,
}

impl SoundManager {
    /// Create a new sound manager with its own audio engine.
    pub fn new() -> Result<Self, AudioError> {
        let engine = AudioEngine::new()?;
        Ok(Self {
            engine: Arc::new(Mutex::new(engine)),
            sounds: Vec::new(),
            groups: Vec::new(),
        })
    }

    /// Create a new sound attached to this manager's engine (routes directly to endpoint).
    pub fn create_sound(&mut self) -> SoundRef {
        self.create_sound_in_group(None)
    }

    /// Create a sound that feeds into the given bus. Pass `None` for the engine endpoint.
    pub fn create_sound_in_group(&mut self, group: Option<SoundGroupRef>) -> SoundRef {
        let sound = Sound::new_in_group(Arc::clone(&self.engine), group)
            .expect("Failed to create sound");
        let sound_ref = Arc::new(Mutex::new(sound));
        self.sounds.push(Arc::downgrade(&sound_ref));
        sound_ref
    }

    /// Create a new sound bus. Pass `None` to attach to the engine endpoint,
    /// or pass another group to nest buses.
    pub fn create_group(&mut self, parent: Option<SoundGroupRef>) -> Result<SoundGroupRef, AudioError> {
        let group = SoundGroup::new(Arc::clone(&self.engine), parent)?;
        let group_ref = Arc::new(Mutex::new(group));
        self.groups.push(Arc::downgrade(&group_ref));
        Ok(group_ref)
    }

    /// Update spatialization for all tracked sounds.
    /// Called internally when listener position or angle changes.
    fn update_all_sounds(&mut self) {
        // Remove dead weak refs and update live ones
        self.sounds.retain(|weak| {
            if let Some(sound_ref) = weak.upgrade() {
                lock(&sound_ref).update_spatialization();
                true
            } else {
                false
            }
        });
    }

    /// Advance pitch tweens on all tracked groups.
    fn tick_groups(&mut self) {
        self.groups.retain(|weak| {
            if let Some(group_ref) = weak.upgrade() {
                lock(&group_ref).advance_pitch_tween();
                true
            } else {
                false
            }
        });
    }

    /// Advance per-sound and per-group automation and refresh spatialization.
    ///
    /// Equivalent to nudging the listener — call this once per frame if you have
    /// active tweens but the listener isn't moving.
    pub fn tick(&mut self) {
        self.tick_groups();
        self.update_all_sounds();
    }

    /// Set the 3D listener position for spatial audio.
    pub fn set_listener_position(&mut self, x: f32, y: f32, z: f32) {
        lock(&self.engine).set_listener_position(x, y, z);
        self.update_all_sounds();
    }

    /// Set the listener facing angle (degrees, unit circle: 0 = +X east, 90 = +Y north/forward).
    pub fn set_listener_angle(&mut self, angle: f32) {
        lock(&self.engine).set_listener_angle(angle);
        self.update_all_sounds();
    }

    /// Set both listener position and angle at once.
    pub fn set_listener(&mut self, x: f32, y: f32, z: f32, angle: f32) {
        if !x.is_finite() || !y.is_finite() || !z.is_finite() || !angle.is_finite() {
            return;
        }
        {
            let mut engine = lock(&self.engine);
            engine.set_listener_position(x, y, z);
            engine.set_listener_angle(angle);
        }
        self.update_all_sounds();
    }

    /// Get the listener X position.
    pub fn listener_x(&self) -> f32 {
        lock(&self.engine).listener_x()
    }

    /// Get the listener Y position.
    pub fn listener_y(&self) -> f32 {
        lock(&self.engine).listener_y()
    }

    /// Get the listener Z position.
    pub fn listener_z(&self) -> f32 {
        lock(&self.engine).listener_z()
    }

    /// Get the listener facing angle in degrees.
    pub fn listener_angle(&self) -> f32 {
        lock(&self.engine).listener_angle()
    }

    /// Check if HRTF (Steam Audio) is available.
    pub fn is_hrtf_available(&self) -> bool {
        lock(&self.engine).is_hrtf_available()
    }

    /// Get the sample rate of the audio engine.
    pub fn sample_rate(&self) -> u32 {
        lock(&self.engine).sample_rate()
    }

    /// Current absolute engine clock in PCM frames.
    pub fn time_in_pcm_frames(&self) -> u64 {
        lock(&self.engine).time_in_pcm_frames()
    }
}

impl Drop for SoundManager {
    fn drop(&mut self) {
        // Sounds are dropped automatically when they go out of scope
        // Engine cleanup is handled by AudioEngine's Drop
    }
}
