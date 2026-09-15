//! Sound class for audio playback with 3D positioning.
//!
//! Supports basic pan/volume positioning or HRTF mode.

use miniaudio_sys::{
    ma_audio_buffer_ref, ma_audio_buffer_ref_init, ma_audio_buffer_ref_uninit, ma_format_f32,
    ma_node_attach_output_bus, ma_node_detach_output_bus, ma_sound, ma_sound_at_end,
    ma_sound_get_cursor_in_pcm_frames, ma_sound_get_length_in_pcm_frames, ma_sound_get_pan,
    ma_sound_init_from_data_source, ma_sound_init_from_file, ma_sound_is_looping,
    ma_sound_is_playing, ma_sound_seek_to_pcm_frame, ma_sound_set_looping, ma_sound_set_pan,
    ma_sound_set_pitch, ma_sound_set_spatialization_enabled, ma_sound_set_volume, ma_sound_start,
    ma_sound_stop, ma_sound_uninit, MA_FALSE, MA_SOUND_FLAG_DECODE, MA_SUCCESS, MA_TRUE,
};
use std::f32::consts::{FRAC_1_SQRT_2, PI};
use std::ffi::{c_void, CString};
use std::mem::MaybeUninit;
use std::ptr;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

use crate::decode::decode_file;
use crate::group::SoundGroupRef;
use crate::stretcher::ola_stretch;
use crate::tween::{Easing, PitchTween};

use crate::engine::AudioEngine;
use crate::error::AudioError;
use crate::phonon_node::{BinauralNode, HrtfInterpolation};
use crate::sync::lock;
use crate::volume::db_to_linear;

// FFI for helper functions
extern "C" {
    fn ma_sound_alloc() -> *mut ma_sound;
    fn ma_sound_free(sound: *mut ma_sound);
    fn ma_sound_get_node_ptr(sound: *mut ma_sound) -> *mut miniaudio_sys::ma_node;
}

/// Backing PCM buffer + miniaudio data-source view, kept alive for the
/// lifetime of a stretched `Sound`. miniaudio reads from this, so the Vec
/// must stay at a stable address — we box it.
struct StretchedBacking {
    // Held to keep the data alive for as long as miniaudio needs it.
    _pcm: Box<[f32]>,
    buffer_ref: Box<ma_audio_buffer_ref>,
}

impl Drop for StretchedBacking {
    fn drop(&mut self) {
        // Tear down the data-source view *before* the PCM drops.
        unsafe { ma_audio_buffer_ref_uninit(&mut *self.buffer_ref) };
    }
}

/// How a sound's pan, volume and pitch are derived.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum SpatialMode {
    /// Pan, volume and pitch are applied exactly as set. The listener and the
    /// sound's position have no effect. Use this for ordinary stereo cues.
    Direct,
    /// Pan and volume are computed from the sound's position relative to the
    /// listener with the pan-step / volume-step model.
    Basic,
    /// Steam Audio HRTF binaural rendering from the sound's position. Falls
    /// back to `Basic` behaviour when HRTF is unavailable.
    Hrtf,
}

/// Sound class for audio playback with 3D positioning.
///
/// Create sounds via `SoundManager::create_sound()` rather than directly.
pub struct Sound {
    sound: *mut ma_sound,
    loaded: bool,
    engine: Arc<Mutex<AudioEngine>>,

    // 3D position as AABB (axis-aligned bounding box)
    // For point sounds, min == max
    min_x: f32,
    min_y: f32,
    min_z: f32,
    max_x: f32,
    max_y: f32,
    max_z: f32,

    // Stationary sounds don't update with listener movement
    stationary: bool,

    // 3D audio parameters
    min_distance: f32,
    max_distance: f32,
    rolloff: f32,
    min_gain: f32,
    max_gain: f32,

    // Horizon-style spatialization parameters
    pan_step: f32,              // Pan amount per unit horizontal distance
    volume_step: f32,           // Volume reduction per unit euclidean distance
    behind_pitch_decrease: f32, // Pitch reduction for sounds behind listener
    hard_close_pan: bool,       // Add extra pan separation for close sounds

    // How pan, volume and pitch are derived: verbatim, from position, or HRTF.
    spatial_mode: SpatialMode,

    // Explicit HRTF rendering policy. This is independent of distance
    // attenuation: blend controls binaural coloration and interpolation
    // controls direction-transition quality.
    hrtf_spatial_blend: f32,
    hrtf_interpolation: HrtfInterpolation,

    // Pan applied verbatim in direct mode and for stationary sounds.
    base_pan: f32,

    // Base volume (before 3D attenuation)
    base_volume: f32,

    // Base pitch (before behind_pitch_decrease adjustment)
    base_pitch: f32,

    // Active pitch tween, if any
    pitch_tween: Option<PitchTween>,

    // Optional bus this sound routes through (instead of engine endpoint).
    group: Option<SoundGroupRef>,

    // When loaded via `load_stretched`, holds the PCM + data-source view.
    stretched_backing: Option<StretchedBacking>,

    // HRTF binaural node
    binaural_node: Option<BinauralNode>,
}

impl Sound {
    /// Create a sound that routes through the given bus instead of the engine endpoint.
    ///
    /// Use `SoundManager::create_sound()` / `create_sound_in_group()` instead of
    /// calling this directly.
    pub(crate) fn new_in_group(
        engine: Arc<Mutex<AudioEngine>>,
        group: Option<SoundGroupRef>,
    ) -> Result<Self, AudioError> {
        let sound = unsafe { ma_sound_alloc() };
        if sound.is_null() {
            return Err(AudioError::AllocationFailed);
        }

        Ok(Self {
            sound,
            loaded: false,
            engine,
            min_x: 0.0,
            min_y: 0.0,
            min_z: 0.0,
            max_x: 0.0,
            max_y: 0.0,
            max_z: 0.0,
            stationary: false,
            min_distance: 1.0,
            max_distance: 100.0,
            rolloff: 1.0,
            min_gain: 0.0,
            max_gain: 1.0,
            pan_step: 0.05,
            volume_step: 0.0333333,
            behind_pitch_decrease: 0.04,
            hard_close_pan: true,
            spatial_mode: SpatialMode::Basic,
            hrtf_spatial_blend: 1.0,
            hrtf_interpolation: HrtfInterpolation::Bilinear,
            base_pan: 0.0,
            base_volume: 1.0,
            base_pitch: 1.0,
            pitch_tween: None,
            group,
            stretched_backing: None,
            binaural_node: None,
        })
    }

    /// Load a sound from a file.
    ///
    /// Sounds are automatically cached - loading the same file multiple times
    /// shares the decoded audio data via miniaudio's resource manager.
    pub fn load(&mut self, filename: &str) -> Result<(), AudioError> {
        // Clean up existing binaural node before reloading
        self.destroy_binaural_node();

        if self.loaded {
            unsafe { ma_sound_uninit(self.sound) };
            self.loaded = false;
        }
        // Any stretched backing from a previous load is no longer referenced.
        self.stretched_backing = None;

        let c_filename =
            CString::new(filename).map_err(|_| AudioError::LoadFailed(filename.to_string()))?;

        let engine_ptr = lock(&self.engine).as_ptr();
        let group_ptr = self
            .group
            .as_ref()
            .map_or(ptr::null_mut(), |g| lock(g).as_ptr());
        let result = unsafe {
            ma_sound_init_from_file(
                engine_ptr,
                c_filename.as_ptr(),
                MA_SOUND_FLAG_DECODE,
                group_ptr,
                ptr::null_mut(),
                self.sound,
            )
        };

        if result == MA_SUCCESS {
            self.loaded = true;
            // Disable miniaudio's built-in spatialization - we handle it ourselves
            unsafe { ma_sound_set_spatialization_enabled(self.sound, MA_FALSE) };

            // Create binaural node if HRTF is already enabled
            if self.spatial_mode == SpatialMode::Hrtf && lock(&self.engine).is_hrtf_available() {
                self.create_binaural_node();
            }

            // Apply pan, volume and pitch set before the load.
            self.update_spatialization();

            Ok(())
        } else {
            Err(AudioError::LoadFailed(filename.to_string()))
        }
    }

    /// Load a sound from a file and time-stretch it by `factor` (pitch preserved).
    ///
    /// `factor > 1.0` makes the sound longer/slower; `factor < 1.0` shorter/faster.
    /// The stretched PCM is held in memory as long as this `Sound` is alive.
    /// Reasonable range: 0.5 .. 3.0. Beyond that, artifacts become audible.
    pub fn load_stretched(&mut self, filename: &str, factor: f32) -> Result<(), AudioError> {
        // Clean up any prior load.
        self.destroy_binaural_node();
        if self.loaded {
            unsafe { ma_sound_uninit(self.sound) };
            self.loaded = false;
        }
        self.stretched_backing = None;

        let engine_sr = lock(&self.engine).sample_rate();
        if engine_sr == 0 {
            return Err(AudioError::LoadFailed(filename.to_string()));
        }

        // Decode the source file at the engine's sample rate, then apply SOLA.
        let decoded = decode_file(filename, engine_sr)?;
        if decoded.samples.is_empty() || decoded.channels == 0 {
            return Err(AudioError::LoadFailed(filename.to_string()));
        }

        let stretched = ola_stretch(
            &decoded.samples,
            decoded.channels as usize,
            decoded.sample_rate,
            factor,
        );
        if stretched.is_empty() {
            return Err(AudioError::LoadFailed(filename.to_string()));
        }

        // Box PCM so the address is stable for miniaudio.
        let pcm: Box<[f32]> = stretched.into_boxed_slice();
        let frames = (pcm.len() / decoded.channels as usize) as u64;

        // Init a non-owning data-source view over the boxed PCM.
        let mut buffer_ref_uninit: Box<MaybeUninit<ma_audio_buffer_ref>> =
            Box::new(MaybeUninit::uninit());
        let r = unsafe {
            ma_audio_buffer_ref_init(
                ma_format_f32,
                decoded.channels,
                pcm.as_ptr() as *const c_void,
                frames,
                buffer_ref_uninit.as_mut_ptr(),
            )
        };
        if r != MA_SUCCESS {
            return Err(AudioError::LoadFailed(filename.to_string()));
        }
        // SAFETY: init returned MA_SUCCESS, buffer_ref is valid.
        let mut buffer_ref: Box<ma_audio_buffer_ref> =
            unsafe { std::mem::transmute(buffer_ref_uninit) };

        // Init the sound from the buffer (which implements ma_data_source).
        let engine_ptr = lock(&self.engine).as_ptr();
        let group_ptr = self
            .group
            .as_ref()
            .map_or(ptr::null_mut(), |g| lock(g).as_ptr());
        let r = unsafe {
            ma_sound_init_from_data_source(
                engine_ptr,
                &mut *buffer_ref as *mut ma_audio_buffer_ref as *mut c_void,
                0, // No decode flag — PCM is already decoded.
                group_ptr,
                self.sound,
            )
        };
        if r != MA_SUCCESS {
            // Tear down the buffer_ref before dropping.
            unsafe { ma_audio_buffer_ref_uninit(&mut *buffer_ref) };
            drop(buffer_ref);
            drop(pcm);
            return Err(AudioError::LoadFailed(filename.to_string()));
        }

        self.loaded = true;
        self.stretched_backing = Some(StretchedBacking {
            _pcm: pcm,
            buffer_ref,
        });

        unsafe { ma_sound_set_spatialization_enabled(self.sound, MA_FALSE) };

        if self.spatial_mode == SpatialMode::Hrtf && lock(&self.engine).is_hrtf_available() {
            self.create_binaural_node();
        }

        // Apply pan, volume and pitch set before the load.
        self.update_spatialization();

        Ok(())
    }

    /// Load a sound from a file and play it reversed (time-reversed PCM).
    ///
    /// The entire file is decoded, the sample frames are reversed in memory,
    /// and the result is played back as a normal sound. Pitch and spatialization
    /// work exactly like `load` / `load_stretched`.
    pub fn load_reversed(&mut self, filename: &str) -> Result<(), AudioError> {
        self.destroy_binaural_node();
        if self.loaded {
            unsafe { ma_sound_uninit(self.sound) };
            self.loaded = false;
        }
        self.stretched_backing = None;

        let engine_sr = lock(&self.engine).sample_rate();
        if engine_sr == 0 {
            return Err(AudioError::LoadFailed(filename.to_string()));
        }

        let decoded = decode_file(filename, engine_sr)?;
        if decoded.samples.is_empty() || decoded.channels == 0 {
            return Err(AudioError::LoadFailed(filename.to_string()));
        }

        // Reverse by frame so channel interleaving is preserved.
        let ch = decoded.channels as usize;
        let mut reversed = decoded.samples;
        let frame_count = reversed.len() / ch;
        for i in 0..frame_count / 2 {
            let j = frame_count - 1 - i;
            for c in 0..ch {
                reversed.swap(i * ch + c, j * ch + c);
            }
        }

        let pcm: Box<[f32]> = reversed.into_boxed_slice();
        let frames = (pcm.len() / ch) as u64;

        let mut buffer_ref_uninit: Box<MaybeUninit<ma_audio_buffer_ref>> =
            Box::new(MaybeUninit::uninit());
        let r = unsafe {
            ma_audio_buffer_ref_init(
                ma_format_f32,
                decoded.channels,
                pcm.as_ptr() as *const c_void,
                frames,
                buffer_ref_uninit.as_mut_ptr(),
            )
        };
        if r != MA_SUCCESS {
            return Err(AudioError::LoadFailed(filename.to_string()));
        }
        // SAFETY: init returned MA_SUCCESS, buffer_ref is valid.
        let mut buffer_ref: Box<ma_audio_buffer_ref> =
            unsafe { std::mem::transmute(buffer_ref_uninit) };

        let engine_ptr = lock(&self.engine).as_ptr();
        let group_ptr = self
            .group
            .as_ref()
            .map_or(ptr::null_mut(), |g| lock(g).as_ptr());
        let r = unsafe {
            ma_sound_init_from_data_source(
                engine_ptr,
                &mut *buffer_ref as *mut ma_audio_buffer_ref as *mut c_void,
                0,
                group_ptr,
                self.sound,
            )
        };
        if r != MA_SUCCESS {
            unsafe { ma_audio_buffer_ref_uninit(&mut *buffer_ref) };
            drop(buffer_ref);
            drop(pcm);
            return Err(AudioError::LoadFailed(filename.to_string()));
        }

        self.loaded = true;
        self.stretched_backing = Some(StretchedBacking {
            _pcm: pcm,
            buffer_ref,
        });

        unsafe { ma_sound_set_spatialization_enabled(self.sound, MA_FALSE) };

        if self.spatial_mode == SpatialMode::Hrtf && lock(&self.engine).is_hrtf_available() {
            self.create_binaural_node();
        }

        // Apply pan, volume and pitch set before the load.
        self.update_spatialization();

        Ok(())
    }

    /// Play the sound.
    pub fn play(&mut self) -> Result<(), AudioError> {
        if !self.loaded {
            return Err(AudioError::NotLoaded);
        }
        let result = unsafe { ma_sound_start(self.sound) };
        if result == MA_SUCCESS {
            Ok(())
        } else {
            Err(AudioError::PlaybackFailed)
        }
    }

    /// Stop the sound and reset to beginning.
    pub fn stop(&mut self) -> Result<(), AudioError> {
        if !self.loaded {
            return Err(AudioError::NotLoaded);
        }
        unsafe {
            ma_sound_stop(self.sound);
            ma_sound_seek_to_pcm_frame(self.sound, 0);
        }
        Ok(())
    }

    /// Pause the sound (maintains position).
    pub fn pause(&mut self) -> Result<(), AudioError> {
        if !self.loaded {
            return Err(AudioError::NotLoaded);
        }
        unsafe { ma_sound_stop(self.sound) };
        Ok(())
    }

    /// Set 3D position as a point (0-width AABB) and update spatialization.
    pub fn set_position(&mut self, x: f32, y: f32, z: f32) {
        if !x.is_finite() || !y.is_finite() || !z.is_finite() {
            return;
        }
        self.min_x = x;
        self.min_y = y;
        self.min_z = z;
        self.max_x = x;
        self.max_y = y;
        self.max_z = z;
        self.update_spatialization();
    }

    /// Set 3D position as a ranged AABB and update spatialization.
    ///
    /// Takes min/max for each axis: min_x, max_x, min_y, max_y, min_z, max_z
    pub fn set_position_ranged(
        &mut self,
        min_x: f32,
        max_x: f32,
        min_y: f32,
        max_y: f32,
        min_z: f32,
        max_z: f32,
    ) {
        if ![min_x, max_x, min_y, max_y, min_z, max_z]
            .iter()
            .all(|coordinate| coordinate.is_finite())
        {
            return;
        }
        (self.min_x, self.max_x) = if min_x <= max_x {
            (min_x, max_x)
        } else {
            (max_x, min_x)
        };
        (self.min_y, self.max_y) = if min_y <= max_y {
            (min_y, max_y)
        } else {
            (max_y, min_y)
        };
        (self.min_z, self.max_z) = if min_z <= max_z {
            (min_z, max_z)
        } else {
            (max_z, min_z)
        };
        self.update_spatialization();
    }

    /// Get the X position (minimum X of AABB).
    pub fn x(&self) -> f32 {
        self.min_x
    }

    /// Get the Y position (minimum Y of AABB).
    pub fn y(&self) -> f32 {
        self.min_y
    }

    /// Get the Z position (minimum Z of AABB).
    pub fn z(&self) -> f32 {
        self.min_z
    }

    /// Get the maximum X of the AABB.
    pub fn max_x(&self) -> f32 {
        self.max_x
    }

    /// Get the maximum Y of the AABB.
    pub fn max_y(&self) -> f32 {
        self.max_y
    }

    /// Get the maximum Z of the AABB.
    pub fn max_z(&self) -> f32 {
        self.max_z
    }

    /// Set whether this sound is stationary (follows the listener with no spatial effects).
    pub fn set_stationary(&mut self, stationary: bool) {
        self.stationary = stationary;
        self.update_spatialization();
    }

    /// Get whether this sound is stationary.
    pub fn is_stationary(&self) -> bool {
        self.stationary
    }

    /// Check if sound is currently playing.
    pub fn is_playing(&self) -> bool {
        if !self.loaded {
            return false;
        }
        unsafe { ma_sound_is_playing(self.sound) == MA_TRUE }
    }

    /// Check if sound has finished playing.
    pub fn at_end(&self) -> bool {
        if !self.loaded {
            return false;
        }
        unsafe { ma_sound_at_end(self.sound) == MA_TRUE }
    }

    /// Get the current playback position in milliseconds.
    pub fn playback_position(&self) -> u64 {
        if !self.loaded {
            return 0;
        }
        let mut cursor: u64 = 0;
        let result = unsafe { ma_sound_get_cursor_in_pcm_frames(self.sound, &mut cursor) };
        if result != MA_SUCCESS {
            return 0;
        }
        let sample_rate = lock(&self.engine).sample_rate();
        if sample_rate == 0 {
            return 0;
        }
        (cursor * 1000) / sample_rate as u64
    }

    /// Set the playback position in milliseconds.
    pub fn set_playback_position(&mut self, position_ms: u64) {
        if !self.loaded {
            return;
        }
        let sample_rate = lock(&self.engine).sample_rate();
        if sample_rate == 0 {
            return;
        }
        let frame_index = (position_ms * sample_rate as u64) / 1000;
        unsafe { ma_sound_seek_to_pcm_frame(self.sound, frame_index) };
    }

    /// Get the total length of the sound in milliseconds.
    pub fn length(&self) -> u64 {
        if !self.loaded {
            return 0;
        }
        let mut length_frames: u64 = 0;
        let result = unsafe { ma_sound_get_length_in_pcm_frames(self.sound, &mut length_frames) };
        if result != MA_SUCCESS {
            return 0;
        }
        let sample_rate = lock(&self.engine).sample_rate();
        if sample_rate == 0 {
            return 0;
        }
        (length_frames * 1000) / sample_rate as u64
    }

    /// Set base volume (0.0 to 1.0) - before 3D attenuation.
    pub fn set_volume(&mut self, volume: f32) {
        if !volume.is_finite() {
            return;
        }
        self.base_volume = volume.clamp(0.0, 1.0);
        self.update_spatialization();
    }

    /// Get base volume.
    pub fn volume(&self) -> f32 {
        self.base_volume
    }

    /// Set pitch (1.0 = normal).
    /// Basic spatialization may further modify it with behind_pitch_decrease;
    /// HRTF mode preserves the authored pitch.
    /// Cancels any running pitch tween.
    pub fn set_pitch(&mut self, pitch: f32) {
        if !pitch.is_finite() || pitch <= 0.0 {
            return;
        }
        self.base_pitch = pitch;
        self.pitch_tween = None;
        self.update_spatialization();
    }

    /// Get base pitch (before behind_pitch_decrease adjustment).
    /// Reflects the current tweened value if a tween is running.
    pub fn pitch(&self) -> f32 {
        self.base_pitch
    }

    /// Start a pitch automation that interpolates from the current pitch to `target`
    /// over `duration` using the given easing curve.
    ///
    /// Useful for slow-motion effects, pitch dives, and other smooth pitch changes.
    /// Replaces any existing tween. The tween advances whenever spatialization is
    /// recomputed (e.g. on listener updates) or via `SoundManager::tick()`.
    pub fn tween_pitch(&mut self, target: f32, duration: Duration, easing: Easing) {
        if !target.is_finite() || target <= 0.0 {
            return;
        }
        // Sample the current value first so a tween starting mid-tween is smooth.
        if let Some(active) = &self.pitch_tween {
            let (current, _) = active.sample();
            self.base_pitch = current;
        }
        self.pitch_tween = Some(PitchTween {
            start_pitch: self.base_pitch,
            target_pitch: target,
            started: Instant::now(),
            duration,
            easing,
        });
        self.update_spatialization();
    }

    /// Cancel any active pitch tween. The pitch holds at its current value.
    pub fn stop_pitch_tween(&mut self) {
        if let Some(active) = &self.pitch_tween {
            let (current, _) = active.sample();
            self.base_pitch = current;
        }
        self.pitch_tween = None;
        self.update_spatialization();
    }

    /// True if a pitch tween is currently running.
    pub fn is_pitch_tweening(&self) -> bool {
        self.pitch_tween.is_some()
    }

    /// Advance any active pitch tween based on wall-clock time.
    /// Returns true if the tween produced a new value (or finished) this call.
    fn advance_pitch_tween(&mut self) -> bool {
        let (value, done) = match &self.pitch_tween {
            Some(tween) => tween.sample(),
            None => return false,
        };
        self.base_pitch = value;
        if done {
            self.pitch_tween = None;
        }
        true
    }

    /// Set pan (-1.0 = left, 0 = center, 1.0 = right).
    ///
    /// Applied verbatim in `SpatialMode::Direct` and for stationary sounds.
    /// In the positional modes the pan is computed from position instead and
    /// this value is only remembered for when the mode changes back.
    pub fn set_pan(&mut self, pan: f32) {
        if !pan.is_finite() {
            return;
        }
        self.base_pan = pan.clamp(-1.0, 1.0);
        self.update_spatialization();
    }

    /// Get the pan currently applied to the sound (the computed pan in the
    /// positional modes, the value set with `set_pan` otherwise).
    pub fn pan(&self) -> f32 {
        if !self.loaded {
            return self.base_pan;
        }
        unsafe { ma_sound_get_pan(self.sound) }
    }

    /// Set looping.
    pub fn set_looping(&mut self, looping: bool) {
        if self.loaded {
            unsafe { ma_sound_set_looping(self.sound, if looping { MA_TRUE } else { MA_FALSE }) };
        }
    }

    /// Get looping state.
    pub fn is_looping(&self) -> bool {
        if !self.loaded {
            return false;
        }
        unsafe { ma_sound_is_looping(self.sound) == MA_TRUE }
    }

    /// Enable/disable HRTF mode.
    ///
    /// True selects `SpatialMode::Hrtf`, false selects `SpatialMode::Basic`.
    pub fn set_hrtf(&mut self, enabled: bool) {
        self.set_spatial_mode(if enabled {
            SpatialMode::Hrtf
        } else {
            SpatialMode::Basic
        });
    }

    /// Get HRTF mode.
    pub fn hrtf(&self) -> bool {
        self.spatial_mode == SpatialMode::Hrtf
    }

    /// Set how pan, volume and pitch are derived. See [`SpatialMode`].
    pub fn set_spatial_mode(&mut self, mode: SpatialMode) {
        if self.spatial_mode == mode {
            return;
        }
        self.spatial_mode = mode;

        if mode == SpatialMode::Hrtf && lock(&self.engine).is_hrtf_available() {
            self.create_binaural_node();
        } else {
            self.destroy_binaural_node();
        }

        self.update_spatialization();
    }

    /// Get the spatial mode.
    pub fn spatial_mode(&self) -> SpatialMode {
        self.spatial_mode
    }

    /// Set the dry/HRTF blend (0 = direct, 1 = fully binaural).
    pub fn set_hrtf_spatial_blend(&mut self, blend: f32) {
        if blend.is_finite() {
            self.hrtf_spatial_blend = blend.clamp(0.0, 1.0);
            self.update_spatialization();
        }
    }

    /// Get the dry/HRTF blend.
    pub fn hrtf_spatial_blend(&self) -> f32 {
        self.hrtf_spatial_blend
    }

    /// Set how Steam Audio interpolates between measured HRTF directions.
    pub fn set_hrtf_interpolation(&mut self, interpolation: HrtfInterpolation) {
        self.hrtf_interpolation = interpolation;
        if let Some(ref mut node) = self.binaural_node {
            node.set_interpolation(interpolation);
        }
    }

    /// Get HRTF interpolation quality.
    pub fn hrtf_interpolation(&self) -> HrtfInterpolation {
        self.hrtf_interpolation
    }

    /// Set minimum distance for 3D falloff.
    /// Sound is at full volume within this distance.
    pub fn set_min_distance(&mut self, distance: f32) {
        if !distance.is_finite() || distance < 0.0 {
            return;
        }
        self.min_distance = distance;
        self.max_distance = self.max_distance.max(distance);
        self.update_spatialization();
    }

    /// Get minimum distance.
    pub fn min_distance(&self) -> f32 {
        self.min_distance
    }

    /// Set maximum distance for 3D falloff.
    /// Sound is silent beyond this distance.
    pub fn set_max_distance(&mut self, distance: f32) {
        if !distance.is_finite() || distance < 0.0 {
            return;
        }
        self.max_distance = distance;
        self.min_distance = self.min_distance.min(distance);
        self.update_spatialization();
    }

    /// Get maximum distance.
    pub fn max_distance(&self) -> f32 {
        self.max_distance
    }

    /// Set rolloff factor for 3D falloff.
    /// Higher values = faster volume dropoff with distance.
    pub fn set_rolloff(&mut self, rolloff: f32) {
        if !rolloff.is_finite() || rolloff < 0.0 {
            return;
        }
        self.rolloff = rolloff;
        self.update_spatialization();
    }

    /// Get rolloff factor.
    pub fn rolloff(&self) -> f32 {
        self.rolloff
    }

    /// Set minimum gain (volume floor).
    pub fn set_min_gain(&mut self, gain: f32) {
        if !gain.is_finite() {
            return;
        }
        self.min_gain = gain.clamp(0.0, 1.0);
        self.max_gain = self.max_gain.max(self.min_gain);
        self.update_spatialization();
    }

    /// Get minimum gain.
    pub fn min_gain(&self) -> f32 {
        self.min_gain
    }

    /// Set maximum gain (volume ceiling).
    pub fn set_max_gain(&mut self, gain: f32) {
        if !gain.is_finite() {
            return;
        }
        self.max_gain = gain.clamp(0.0, 1.0);
        self.min_gain = self.min_gain.min(self.max_gain);
        self.update_spatialization();
    }

    /// Get maximum gain.
    pub fn max_gain(&self) -> f32 {
        self.max_gain
    }

    /// Set pan step (pan amount per unit horizontal distance, default 0.05).
    pub fn set_pan_step(&mut self, step: f32) {
        if !step.is_finite() || step < 0.0 {
            return;
        }
        self.pan_step = step;
        self.update_spatialization();
    }

    /// Get pan step.
    pub fn pan_step(&self) -> f32 {
        self.pan_step
    }

    /// Set volume step (volume reduction per unit distance, default 0.0333).
    pub fn set_volume_step(&mut self, step: f32) {
        if !step.is_finite() || step < 0.0 {
            return;
        }
        self.volume_step = step;
        self.update_spatialization();
    }

    /// Get volume step.
    pub fn volume_step(&self) -> f32 {
        self.volume_step
    }

    /// Set behind pitch decrease (pitch reduction for sounds behind listener, default 0.04).
    pub fn set_behind_pitch_decrease(&mut self, decrease: f32) {
        if !decrease.is_finite() || decrease < 0.0 {
            return;
        }
        self.behind_pitch_decrease = decrease;
        self.update_spatialization();
    }

    /// Get behind pitch decrease.
    pub fn behind_pitch_decrease(&self) -> f32 {
        self.behind_pitch_decrease
    }

    /// Set hard close pan (add extra pan separation for close sounds, default true).
    pub fn set_hard_close_pan(&mut self, enabled: bool) {
        self.hard_close_pan = enabled;
        self.update_spatialization();
    }

    /// Get hard close pan setting.
    pub fn hard_close_pan(&self) -> bool {
        self.hard_close_pan
    }

    // Private helper methods

    /// Resolve the graph node this sound should ultimately feed:
    /// its bus if one is set, otherwise the engine endpoint.
    fn downstream_node_ptr(&self) -> *mut miniaudio_sys::ma_node {
        if let Some(g) = self.group.as_ref() {
            lock(g).as_ptr() as *mut miniaudio_sys::ma_node
        } else {
            lock(&self.engine).get_endpoint() as *mut miniaudio_sys::ma_node
        }
    }

    fn create_binaural_node(&mut self) {
        if self.binaural_node.is_some() || !lock(&self.engine).is_hrtf_available() || !self.loaded
        {
            return;
        }

        let node_graph = lock(&self.engine).get_node_graph();
        let downstream = self.downstream_node_ptr();

        match BinauralNode::new(node_graph, 2) {
            Ok(mut node) => {
                node.set_interpolation(self.hrtf_interpolation);
                node.set_spatial_blend(self.hrtf_spatial_blend);
                let sound_node = unsafe { ma_sound_get_node_ptr(self.sound) };
                if !sound_node.is_null() {
                    unsafe {
                        ma_node_detach_output_bus(sound_node, 0);
                        ma_node_attach_output_bus(
                            sound_node, 0, node.as_ptr() as *mut _, 0,
                        );
                        ma_node_attach_output_bus(
                            node.as_ptr() as *mut _, 0, downstream, 0,
                        );
                    }
                }
                self.binaural_node = Some(node);
            }
            Err(_) => {
                // Failed to create binaural node, continue without HRTF
            }
        }
    }

    fn destroy_binaural_node(&mut self) {
        if self.binaural_node.take().is_some() && self.loaded {
            let sound_node = unsafe { ma_sound_get_node_ptr(self.sound) };
            let downstream = self.downstream_node_ptr();
            if !sound_node.is_null() {
                unsafe {
                    ma_node_detach_output_bus(sound_node, 0);
                    ma_node_attach_output_bus(sound_node, 0, downstream, 0);
                }
            }
        }
    }

    /// Get the closest point on the AABB to the listener.
    fn closest_point_on_aabb(&self) -> (f32, f32, f32) {
        let engine = lock(&self.engine);
        let lx = engine.listener_x();
        let ly = engine.listener_y();
        let lz = engine.listener_z();
        (
            lx.clamp(self.min_x, self.max_x),
            ly.clamp(self.min_y, self.max_y),
            lz.clamp(self.min_z, self.max_z),
        )
    }

    /// Update spatialization (pan and volume) based on position.
    /// Called internally when sound properties change, or by SoundManager when listener moves.
    pub fn update_spatialization(&mut self) {
        if !self.loaded {
            return;
        }

        // Advance any active pitch automation before we read base_pitch below.
        self.advance_pitch_tween();

        if self.stationary || self.spatial_mode == SpatialMode::Direct {
            // Direct mode and stationary sounds: pan, volume and pitch are
            // applied verbatim and the listener has no effect.
            unsafe {
                ma_sound_set_pan(self.sound, self.base_pan);
                ma_sound_set_volume(self.sound, self.base_volume);
                ma_sound_set_pitch(self.sound, self.base_pitch);
            }

            // A stationary HRTF sound follows the listener and is deliberately
            // dry. A full-strength front HRTF is not a transparent pass-through.
            if let Some(ref mut node) = self.binaural_node {
                node.set_spatial_parameters(0.0, 0.0, -1.0, 0.0);
            }
            return;
        }

        if self.spatial_mode == SpatialMode::Hrtf && self.binaural_node.is_some() {
            self.update_hrtf_spatialization();
        } else {
            self.update_basic_spatialization();
        }
    }

    fn update_hrtf_spatialization(&mut self) {
        let engine = lock(&self.engine);
        let listener_x = engine.listener_x();
        let listener_y = engine.listener_y();
        let listener_z = engine.listener_z();
        let listener_angle = engine.listener_angle();
        drop(engine);

        let (edge_x, edge_y, edge_z) = self.closest_point_on_aabb();

        // Calculate direction vector from listener to closest edge
        let dx = edge_x - listener_x;
        let dy = edge_y - listener_y;
        let dz = edge_z - listener_z;

        let distance = (dx * dx + dy * dy + dz * dz).sqrt();

        // Rotate horizontal direction by listener angle
        let rot_angle = (-listener_angle + 90.0) * (PI / 180.0);
        let cos_rot = rot_angle.cos();
        let sin_rot = rot_angle.sin();
        let rot_x = dx * cos_rot - dy * sin_rot;
        let rot_y = dx * sin_rot + dy * cos_rot;

        // Transform to Steam Audio coordinates: X=right, Y=up, -Z=forward
        let steam_x = rot_x;
        let steam_y = dz;
        let steam_z = -rot_y;

        // Normalize direction
        let (steam_x, steam_y, steam_z) = if distance > 0.0001 {
            (steam_x / distance, steam_y / distance, steam_z / distance)
        } else {
            (0.0, 0.0, -1.0) // Default to forward
        };

        // Update binaural node direction
        if let Some(ref mut node) = self.binaural_node {
            node.set_spatial_parameters(
                steam_x,
                steam_y,
                steam_z,
                if distance > 1e-4 {
                    self.hrtf_spatial_blend
                } else {
                    0.0
                },
            );
        }

        // Apply volume attenuation based on distance
        let attenuated_distance = (distance - self.min_distance).max(0.0);
        let volume = if attenuated_distance <= self.max_distance - self.min_distance {
            db_to_linear(-attenuated_distance * self.rolloff * 1.75)
        } else {
            0.0
        };
        let volume = volume.clamp(self.min_gain, self.max_gain) * self.base_volume;
        unsafe { ma_sound_set_volume(self.sound, volume) };

        // Clear pan since HRTF handles spatialization
        unsafe { ma_sound_set_pan(self.sound, 0.0) };

        // HRTF already supplies the spectral cues for front/back and
        // elevation. Pitch remains an authored property, consistent with Web
        // Audio HRTF and without detuning sources as they move behind us.
        unsafe { ma_sound_set_pitch(self.sound, self.base_pitch) };
    }

    fn update_basic_spatialization(&mut self) {
        let engine = lock(&self.engine);
        let listener_x = engine.listener_x();
        let listener_y = engine.listener_y();
        let listener_z = engine.listener_z();
        let listener_angle = engine.listener_angle();
        drop(engine);

        let (edge_x, edge_y, edge_z) = self.closest_point_on_aabb();

        let dx = edge_x - listener_x;
        let dy = edge_y - listener_y;
        let dz = edge_z - listener_z;

        let distance = (dx * dx + dy * dy + dz * dz).sqrt();
        let horizontal_distance = (dx * dx + dy * dy).sqrt();

        // Rotate relative position by listener angle
        let rot_angle = (-listener_angle + 90.0) * (PI / 180.0);
        let cos_rot = rot_angle.cos();
        let sin_rot = rot_angle.sin();
        let rot_x = dx * cos_rot - dy * sin_rot;
        let rot_y = dx * sin_rot + dy * cos_rot;

        // Calculate pan using angle-based method
        const EPSILON: f32 = 1e-4;
        let pan = if horizontal_distance > EPSILON {
            let azimuth = rot_y.atan2(rot_x);
            let angle_factor = azimuth.cos();
            let mut distance_factor = horizontal_distance * self.pan_step;

            if self.hard_close_pan && distance > EPSILON {
                distance_factor += 0.2;
            }

            (angle_factor * distance_factor.clamp(-1.0, 1.0)).clamp(-1.0, 1.0)
        } else {
            0.0
        };

        unsafe { ma_sound_set_pan(self.sound, pan) };

        // Calculate volume based on distance
        let volume = (1.0 - distance * self.volume_step).clamp(self.min_gain, self.max_gain)
            * self.base_volume;
        unsafe { ma_sound_set_volume(self.sound, volume) };

        // Behind pitch decrease (applied to base_pitch)
        let mut pitch = self.base_pitch;
        if distance > FRAC_1_SQRT_2 + EPSILON {
            if rot_y < -EPSILON {
                pitch -= self.behind_pitch_decrease;
            }
            if dz < -EPSILON {
                pitch -= self.behind_pitch_decrease;
            }
        }
        unsafe { ma_sound_set_pitch(self.sound, pitch.max(0.01)) };
    }
}

impl Drop for Sound {
    fn drop(&mut self) {
        // Clean up binaural node first
        self.destroy_binaural_node();

        if !self.sound.is_null() {
            if self.loaded {
                unsafe { ma_sound_uninit(self.sound) };
            }
            unsafe { ma_sound_free(self.sound) };
        }
    }
}

// SAFETY: a `Sound` is only ever reached through the `Mutex` in its `SoundRef`,
// so one caller thread at a time touches its `ma_sound`, binaural node and
// stretched PCM. miniaudio's sound property setters, start and stop are
// documented as safe to call from any thread. Binaural parameters are
// published to the audio thread through a lock-free atomic snapshot.
unsafe impl Send for Sound {}
