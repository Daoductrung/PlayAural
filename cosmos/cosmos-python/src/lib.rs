//! Python bindings for Cosmos audio game library.
//!
//! Provides PyO3-based Python bindings matching the existing cffi API.

use pyo3::prelude::*;
use pyo3::exceptions::{PyRuntimeError, PyValueError};

use cosmos_audio::{
    Easing, HrtfInterpolation, SoundGroupRef, SoundManager as RustSoundManager, SoundRef,
    SpatialMode,
};
use cosmos_screenreader::ScreenReader as RustScreenReader;
use cosmos_window::{Window as RustWindow, Key as RustKey};

use std::sync::{Arc, Mutex, MutexGuard};
use std::time::Duration;

/// Lock an audio object, recovering the guard if a previous holder panicked.
fn lock<T>(mutex: &Mutex<T>) -> MutexGuard<'_, T> {
    mutex.lock().unwrap_or_else(|poisoned| poisoned.into_inner())
}

fn parse_spatial_mode(name: &str) -> PyResult<SpatialMode> {
    match name.to_ascii_lowercase().as_str() {
        "direct" => Ok(SpatialMode::Direct),
        "basic" => Ok(SpatialMode::Basic),
        "hrtf" => Ok(SpatialMode::Hrtf),
        other => Err(PyValueError::new_err(format!(
            "Unknown spatial mode '{}'. Expected one of: direct, basic, hrtf",
            other
        ))),
    }
}

fn spatial_mode_name(mode: SpatialMode) -> &'static str {
    match mode {
        SpatialMode::Direct => "direct",
        SpatialMode::Basic => "basic",
        SpatialMode::Hrtf => "hrtf",
    }
}

fn parse_hrtf_interpolation(name: &str) -> PyResult<HrtfInterpolation> {
    match name.to_ascii_lowercase().as_str() {
        "nearest" => Ok(HrtfInterpolation::Nearest),
        "bilinear" => Ok(HrtfInterpolation::Bilinear),
        other => Err(PyValueError::new_err(format!(
            "Unknown HRTF interpolation '{}'. Expected one of: nearest, bilinear",
            other
        ))),
    }
}

fn hrtf_interpolation_name(interpolation: HrtfInterpolation) -> &'static str {
    match interpolation {
        HrtfInterpolation::Nearest => "nearest",
        HrtfInterpolation::Bilinear => "bilinear",
    }
}

fn parse_easing(name: &str) -> PyResult<Easing> {
    match name.to_ascii_lowercase().as_str() {
        "linear" => Ok(Easing::Linear),
        "ease_in" | "easein" | "in" => Ok(Easing::EaseIn),
        "ease_out" | "easeout" | "out" => Ok(Easing::EaseOut),
        "ease_in_out" | "easeinout" | "in_out" | "inout" => Ok(Easing::EaseInOut),
        other => Err(PyValueError::new_err(format!(
            "Unknown easing '{}'. Expected one of: linear, ease_in, ease_out, ease_in_out",
            other
        ))),
    }
}

/// Sound class for audio playback with 3D positioning. Safe to use from any
/// thread; calls are serialised on the sound's own lock.
#[pyclass]
struct Sound {
    inner: SoundRef,
}

#[pymethods]
impl Sound {
    /// Load audio from a file. Returns True on success.
    fn load(&mut self, filename: &str) -> PyResult<bool> {
        match lock(&self.inner).load(filename) {
            Ok(()) => Ok(true),
            Err(_) => Ok(false),
        }
    }

    /// Load audio from a file and time-stretch it by `factor` (pitch preserved).
    ///
    /// `factor > 1.0` = longer/slower; `factor < 1.0` = shorter/faster.
    /// Useful for screams, sustained vocals, and any place you want to alter
    /// duration without changing pitch. Internally decodes the file, applies
    /// SOLA in Rust, and keeps the stretched PCM alive for the sound's lifetime.
    /// Returns True on success.
    fn load_stretched(&mut self, filename: &str, factor: f32) -> PyResult<bool> {
        match lock(&self.inner).load_stretched(filename, factor) {
            Ok(()) => Ok(true),
            Err(_) => Ok(false),
        }
    }

    /// Load audio from a file and prepare it for reversed playback.
    ///
    /// Decodes the file, reverses the PCM frames in memory, and plays the result
    /// as a normal sound. Pitch, tween_pitch, and 3D spatialization all work
    /// exactly as with `load`. Returns True on success.
    fn load_reversed(&mut self, filename: &str) -> PyResult<bool> {
        match lock(&self.inner).load_reversed(filename) {
            Ok(()) => Ok(true),
            Err(_) => Ok(false),
        }
    }

    /// Start playing the sound.
    fn play(&mut self) -> PyResult<bool> {
        match lock(&self.inner).play() {
            Ok(()) => Ok(true),
            Err(_) => Ok(false),
        }
    }

    /// Stop playing and reset to the beginning.
    fn stop(&mut self) -> PyResult<bool> {
        match lock(&self.inner).stop() {
            Ok(()) => Ok(true),
            Err(_) => Ok(false),
        }
    }

    /// Pause playback (maintains position).
    fn pause(&mut self) -> PyResult<bool> {
        match lock(&self.inner).pause() {
            Ok(()) => Ok(true),
            Err(_) => Ok(false),
        }
    }

    /// Check if the sound is currently playing.
    #[getter]
    fn playing(&self) -> bool {
        lock(&self.inner).is_playing()
    }

    /// Check if the sound has finished playing.
    #[getter]
    fn at_end(&self) -> bool {
        lock(&self.inner).at_end()
    }

    /// Get the current playback position in milliseconds.
    #[getter]
    fn playback_position(&self) -> u64 {
        lock(&self.inner).playback_position()
    }

    /// Set the playback position in milliseconds.
    #[setter]
    fn set_playback_position(&mut self, value: u64) {
        lock(&self.inner).set_playback_position(value);
    }

    /// Get the total length of the sound in milliseconds.
    #[getter]
    fn length(&self) -> u64 {
        lock(&self.inner).length()
    }

    /// Set the 3D position of this sound as a point source.
    fn set_position(&mut self, x: f32, y: f32, z: f32) {
        lock(&self.inner).set_position(x, y, z);
    }

    /// Set the 3D position as a ranged AABB.
    fn set_position_ranged(&mut self, minx: f32, maxx: f32, miny: f32, maxy: f32, minz: f32, maxz: f32) {
        lock(&self.inner).set_position_ranged(minx, maxx, miny, maxy, minz, maxz);
    }

    /// Get the current 3D position as (x, y, z) tuple.
    #[getter]
    fn position(&self) -> (f32, f32, f32) {
        let s = lock(&self.inner);
        (s.x(), s.y(), s.z())
    }

    /// Set the 3D position from (x, y, z) tuple.
    #[setter(position)]
    fn set_position_tuple(&mut self, value: (f32, f32, f32)) {
        lock(&self.inner).set_position(value.0, value.1, value.2);
    }

    /// Get the AABB bounds as (minx, maxx, miny, maxy, minz, maxz).
    #[getter]
    fn position_ranged(&self) -> (f32, f32, f32, f32, f32, f32) {
        let s = lock(&self.inner);
        (
            s.x(),
            s.max_x(),
            s.y(),
            s.max_y(),
            s.z(),
            s.max_z(),
        )
    }

    /// Get X position.
    #[getter]
    fn x(&self) -> f32 {
        lock(&self.inner).x()
    }

    /// Get Y position.
    #[getter]
    fn y(&self) -> f32 {
        lock(&self.inner).y()
    }

    /// Get Z position.
    #[getter]
    fn z(&self) -> f32 {
        lock(&self.inner).z()
    }

    /// Get/set whether this sound is stationary.
    #[getter]
    fn stationary(&self) -> bool {
        lock(&self.inner).is_stationary()
    }

    #[setter]
    fn set_stationary(&mut self, value: bool) {
        lock(&self.inner).set_stationary(value);
    }

    /// Get/set volume (0.0 to 1.0).
    #[getter]
    fn volume(&self) -> f32 {
        lock(&self.inner).volume()
    }

    #[setter]
    fn set_volume(&mut self, value: f32) {
        lock(&self.inner).set_volume(value);
    }

    /// Get/set pitch (1.0 = normal). Setting cancels any active pitch tween.
    #[getter]
    fn pitch(&self) -> f32 {
        lock(&self.inner).pitch()
    }

    #[setter]
    fn set_pitch(&mut self, value: f32) {
        lock(&self.inner).set_pitch(value);
    }

    /// Smoothly interpolate pitch to `target` over `duration_ms` milliseconds.
    ///
    /// Easing options: "linear", "ease_in", "ease_out", "ease_in_out".
    /// Useful for slow-motion, pitch dives, and other smooth pitch changes.
    /// The tween advances on each listener update (or via `SoundManager.tick()`).
    /// Replaces any existing tween. Setting `pitch` directly cancels the tween.
    #[pyo3(signature = (target, duration_ms, easing = "linear"))]
    fn tween_pitch(&mut self, target: f32, duration_ms: u64, easing: &str) -> PyResult<()> {
        let easing = parse_easing(easing)?;
        lock(&self.inner)
            .tween_pitch(target, Duration::from_millis(duration_ms), easing);
        Ok(())
    }

    /// Cancel any running pitch tween. Pitch holds at its current value.
    fn stop_pitch_tween(&mut self) {
        lock(&self.inner).stop_pitch_tween();
    }

    /// True if a pitch tween is currently running.
    #[getter]
    fn is_pitch_tweening(&self) -> bool {
        lock(&self.inner).is_pitch_tweening()
    }

    /// Get/set pan (-1.0 = left, 0 = center, 1.0 = right).
    #[getter]
    fn pan(&self) -> f32 {
        lock(&self.inner).pan()
    }

    #[setter]
    fn set_pan(&mut self, value: f32) {
        lock(&self.inner).set_pan(value);
    }

    /// Get/set whether the sound loops.
    #[getter]
    fn looping(&self) -> bool {
        lock(&self.inner).is_looping()
    }

    #[setter]
    fn set_looping(&mut self, value: bool) {
        lock(&self.inner).set_looping(value);
    }

    /// Get/set HRTF (3D audio) mode.
    #[getter]
    fn hrtf(&self) -> bool {
        lock(&self.inner).hrtf()
    }

    #[setter]
    fn set_hrtf(&mut self, value: bool) {
        lock(&self.inner).set_hrtf(value);
    }

    /// Get/set how pan, volume and pitch are derived:
    /// "direct" applies them exactly as set (ordinary stereo cues),
    /// "basic" computes pan and volume from the sound's position, and
    /// "hrtf" renders the position binaurally through Steam Audio.
    #[getter]
    fn spatial_mode(&self) -> &'static str {
        spatial_mode_name(lock(&self.inner).spatial_mode())
    }

    #[setter]
    fn set_spatial_mode(&mut self, value: &str) -> PyResult<()> {
        let mode = parse_spatial_mode(value)?;
        lock(&self.inner).set_spatial_mode(mode);
        Ok(())
    }

    /// Get/set the dry/HRTF blend (0.0 = direct, 1.0 = fully binaural).
    #[getter]
    fn hrtf_spatial_blend(&self) -> f32 {
        lock(&self.inner).hrtf_spatial_blend()
    }

    #[setter]
    fn set_hrtf_spatial_blend(&mut self, value: f32) {
        lock(&self.inner).set_hrtf_spatial_blend(value);
    }

    /// Get/set HRTF direction interpolation: "nearest" or "bilinear".
    #[getter]
    fn hrtf_interpolation(&self) -> &'static str {
        hrtf_interpolation_name(lock(&self.inner).hrtf_interpolation())
    }

    #[setter]
    fn set_hrtf_interpolation(&mut self, value: &str) -> PyResult<()> {
        let interpolation = parse_hrtf_interpolation(value)?;
        lock(&self.inner).set_hrtf_interpolation(interpolation);
        Ok(())
    }

    /// Get/set minimum distance for 3D falloff.
    #[getter]
    fn min_distance(&self) -> f32 {
        lock(&self.inner).min_distance()
    }

    #[setter]
    fn set_min_distance(&mut self, value: f32) {
        lock(&self.inner).set_min_distance(value);
    }

    /// Get/set maximum distance for 3D falloff.
    #[getter]
    fn max_distance(&self) -> f32 {
        lock(&self.inner).max_distance()
    }

    #[setter]
    fn set_max_distance(&mut self, value: f32) {
        lock(&self.inner).set_max_distance(value);
    }

    /// Get/set rolloff factor for distance attenuation.
    #[getter]
    fn rolloff(&self) -> f32 {
        lock(&self.inner).rolloff()
    }

    #[setter]
    fn set_rolloff(&mut self, value: f32) {
        lock(&self.inner).set_rolloff(value);
    }

    /// Get/set the lower bound applied by Cosmos distance attenuation.
    #[getter]
    fn min_gain(&self) -> f32 {
        lock(&self.inner).min_gain()
    }

    #[setter]
    fn set_min_gain(&mut self, value: f32) {
        lock(&self.inner).set_min_gain(value);
    }

    /// Get/set the upper bound applied by Cosmos distance attenuation.
    #[getter]
    fn max_gain(&self) -> f32 {
        lock(&self.inner).max_gain()
    }

    #[setter]
    fn set_max_gain(&mut self, value: f32) {
        lock(&self.inner).set_max_gain(value);
    }

    /// Get/set pan step.
    #[getter]
    fn pan_step(&self) -> f32 {
        lock(&self.inner).pan_step()
    }

    #[setter]
    fn set_pan_step(&mut self, value: f32) {
        lock(&self.inner).set_pan_step(value);
    }

    /// Get/set volume step.
    #[getter]
    fn volume_step(&self) -> f32 {
        lock(&self.inner).volume_step()
    }

    #[setter]
    fn set_volume_step(&mut self, value: f32) {
        lock(&self.inner).set_volume_step(value);
    }

    /// Get/set behind pitch decrease.
    #[getter]
    fn behind_pitch_decrease(&self) -> f32 {
        lock(&self.inner).behind_pitch_decrease()
    }

    #[setter]
    fn set_behind_pitch_decrease(&mut self, value: f32) {
        lock(&self.inner).set_behind_pitch_decrease(value);
    }

    /// Get/set hard close pan.
    #[getter]
    fn hard_close_pan(&self) -> bool {
        lock(&self.inner).hard_close_pan()
    }

    #[setter]
    fn set_hard_close_pan(&mut self, value: bool) {
        lock(&self.inner).set_hard_close_pan(value);
    }
}

/// A sound bus. Feeds a group of sounds into a single node that can have
/// its own volume, pitch, and pitch automation applied.
#[pyclass]
struct SoundGroup {
    inner: SoundGroupRef,
}

#[pymethods]
impl SoundGroup {
    /// Get/set bus volume (0.0 to 1.0).
    #[getter]
    fn volume(&self) -> f32 {
        lock(&self.inner).volume()
    }

    #[setter]
    fn set_volume(&mut self, value: f32) {
        lock(&self.inner).set_volume(value);
    }

    /// Get/set bus pitch (1.0 = normal). Setting cancels any active tween.
    #[getter]
    fn pitch(&self) -> f32 {
        lock(&self.inner).pitch()
    }

    #[setter]
    fn set_pitch(&mut self, value: f32) {
        lock(&self.inner).set_pitch(value);
    }

    /// Smoothly interpolate bus pitch to `target` over `duration_ms` milliseconds.
    ///
    /// Easing options: "linear", "ease_in", "ease_out", "ease_in_out".
    /// The tween advances whenever `SoundManager.tick()` or the listener moves.
    #[pyo3(signature = (target, duration_ms, easing = "linear"))]
    fn tween_pitch(&mut self, target: f32, duration_ms: u64, easing: &str) -> PyResult<()> {
        let easing = parse_easing(easing)?;
        lock(&self.inner)
            .tween_pitch(target, Duration::from_millis(duration_ms), easing);
        Ok(())
    }

    /// Cancel any running pitch tween on this bus.
    fn stop_pitch_tween(&mut self) {
        lock(&self.inner).stop_pitch_tween();
    }

    /// True if a pitch tween is currently running on this bus.
    #[getter]
    fn is_pitch_tweening(&self) -> bool {
        lock(&self.inner).is_pitch_tweening()
    }

    /// Start playback on the whole bus (starts all contained sounds).
    fn play(&mut self) {
        lock(&self.inner).play();
    }

    /// Stop playback on the whole bus (stops all contained sounds).
    fn stop(&mut self) {
        lock(&self.inner).stop();
    }

    /// Enable a convolution (impulse-response) reverb on this bus.
    ///
    /// * `wet`      — reverb tail level in the output [0,1]
    /// * `dry`      — direct-signal level in the output [0,1]
    /// * `predelay` — milliseconds before the wet onset [0,250]
    /// * `ir_gain`  — wet makeup gain [0,4]
    /// * `width`    — stereo width of the wet (0 = mono, 1 = full, up to 2)
    /// * `decay`    — tail-shaping; 1.0 = IR unchanged, smaller = shorter [0.05,1]
    /// * `lowcut`   — high-pass on the wet, Hz
    /// * `highcut`  — low-pass on the wet, Hz
    /// * `diffuse`  — 0 = wet follows the source's pan, 1 = mono send → diffuse
    ///               tail that does NOT pan with the source (the dry stays
    ///               spatialized either way)
    ///
    /// Defaults to a built-in synthetic IR; call `set_reverb_ir(path)` to load
    /// a custom impulse response. Re-calling this updates params in place.
    #[pyo3(signature = (wet = 0.33, dry = 1.0, predelay = 0.0, ir_gain = 1.0,
                        width = 1.0, decay = 1.0, lowcut = 20.0, highcut = 18000.0,
                        diffuse = 1.0))]
    #[allow(clippy::too_many_arguments)]
    fn enable_reverb(
        &mut self,
        wet: f32,
        dry: f32,
        predelay: f32,
        ir_gain: f32,
        width: f32,
        decay: f32,
        lowcut: f32,
        highcut: f32,
        diffuse: f32,
    ) -> PyResult<()> {
        lock(&self.inner)
            .enable_reverb(wet, dry, predelay, ir_gain, width, decay, lowcut, highcut, diffuse)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to enable reverb: {:?}", e)))
    }

    /// Remove the reverb from this bus.
    fn disable_reverb(&mut self) {
        lock(&self.inner).disable_reverb();
    }

    /// Check whether reverb is currently active on this bus.
    #[getter]
    fn has_reverb(&self) -> bool {
        lock(&self.inner).has_reverb()
    }

    /// Update reverb parameters without toggling enable state. No-op if
    /// reverb isn't currently enabled.
    #[pyo3(signature = (wet, dry, predelay, ir_gain, width, decay, lowcut, highcut, diffuse))]
    #[allow(clippy::too_many_arguments)]
    fn set_reverb_params(&mut self, wet: f32, dry: f32, predelay: f32, ir_gain: f32,
                         width: f32, decay: f32, lowcut: f32, highcut: f32, diffuse: f32) {
        lock(&self.inner)
            .set_reverb_params(wet, dry, predelay, ir_gain, width, decay, lowcut, highcut, diffuse);
    }

    /// Current reverb parameters as
    /// (wet, dry, predelay, ir_gain, width, decay, lowcut, highcut, diffuse),
    /// or None if reverb isn't enabled.
    #[getter]
    fn reverb_params(&self) -> Option<(f32, f32, f32, f32, f32, f32, f32, f32, f32)> {
        lock(&self.inner).reverb_params()
    }

    /// Load a custom impulse response from any decodable audio file
    /// (wav/ogg/flac/mp3). It's resampled to the engine rate and folded to
    /// stereo. Returns True on success. No-op (False) if reverb isn't enabled.
    fn set_reverb_ir(&mut self, path: &str) -> bool {
        lock(&self.inner).set_reverb_ir(path)
    }

    /// Restore the built-in synthetic IR. Returns True on success.
    fn reset_reverb_ir(&mut self) -> bool {
        lock(&self.inner).reset_reverb_ir()
    }

    // --- EQ ---------------------------------------------------------

    /// Enable a 3-band EQ on this bus. Gains are in dB (-24 to +24),
    /// frequencies in Hz. `mid_q` is the Q of the mid peak (default 1.0).
    #[pyo3(signature = (
        low_gain = 0.0, mid_gain = 0.0, high_gain = 0.0,
        low_freq = 200.0, mid_freq = 2000.0, high_freq = 5000.0, mid_q = 1.0
    ))]
    fn enable_eq(
        &mut self,
        low_gain: f32, mid_gain: f32, high_gain: f32,
        low_freq: f32, mid_freq: f32, high_freq: f32, mid_q: f32,
    ) -> PyResult<()> {
        lock(&self.inner)
            .enable_eq(low_gain, mid_gain, high_gain, low_freq, mid_freq, high_freq, mid_q)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to enable EQ: {:?}", e)))
    }

    fn disable_eq(&mut self) { lock(&self.inner).disable_eq(); }

    #[getter]
    fn has_eq(&self) -> bool { lock(&self.inner).has_eq() }

    fn set_eq_params(
        &mut self,
        low_gain: f32, mid_gain: f32, high_gain: f32,
        low_freq: f32, mid_freq: f32, high_freq: f32, mid_q: f32,
    ) {
        lock(&self.inner).set_eq_params(
            low_gain, mid_gain, high_gain, low_freq, mid_freq, high_freq, mid_q
        );
    }

    /// (low_gain_db, mid_gain_db, high_gain_db, low_freq, mid_freq, high_freq, mid_q)
    /// or None if EQ isn't enabled.
    #[getter]
    fn eq_params(&self) -> Option<(f32, f32, f32, f32, f32, f32, f32)> {
        lock(&self.inner).eq_params()
    }

    // --- Disperser --------------------------------------------------

    /// Enable a phase disperser on this bus. `freq` is the center frequency,
    /// `q` the bandwidth of each allpass, `stages` the cascade count (1-32).
    #[pyo3(signature = (freq = 800.0, q = 0.707, stages = 8))]
    fn enable_disperser(&mut self, freq: f32, q: f32, stages: i32) -> PyResult<()> {
        lock(&self.inner)
            .enable_disperser(freq, q, stages)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to enable disperser: {:?}", e)))
    }

    fn disable_disperser(&mut self) { lock(&self.inner).disable_disperser(); }

    #[getter]
    fn has_disperser(&self) -> bool { lock(&self.inner).has_disperser() }

    fn set_disperser_params(&mut self, freq: f32, q: f32, stages: i32) {
        lock(&self.inner).set_disperser_params(freq, q, stages);
    }

    /// (freq, q, stages) or None if disperser isn't enabled.
    #[getter]
    fn disperser_params(&self) -> Option<(f32, f32, i32)> {
        lock(&self.inner).disperser_params()
    }

    // --- Filter (multimode biquad) ----------------------------------

    /// Enable a multimode biquad filter on this bus. `mode` selects the
    /// response: 0=lowpass 1=highpass 2=bandpass 3=notch 4=peak 5=lowshelf
    /// 6=highshelf 7=allpass. `freq` is the cutoff/center (Hz), `q` the
    /// resonance, `gain` the dB gain used by peak/shelf modes.
    #[pyo3(signature = (mode = 0, freq = 1000.0, q = 0.707, gain = 0.0))]
    fn enable_filter(&mut self, mode: i32, freq: f32, q: f32, gain: f32) -> PyResult<()> {
        lock(&self.inner)
            .enable_filter(mode, freq, q, gain)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to enable filter: {:?}", e)))
    }

    fn disable_filter(&mut self) { lock(&self.inner).disable_filter(); }

    #[getter]
    fn has_filter(&self) -> bool { lock(&self.inner).has_filter() }

    fn set_filter_params(&mut self, mode: i32, freq: f32, q: f32, gain: f32) {
        lock(&self.inner).set_filter_params(mode, freq, q, gain);
    }

    /// (mode, freq, q, gain) or None if the filter isn't enabled.
    #[getter]
    fn filter_params(&self) -> Option<(i32, f32, f32, f32)> {
        lock(&self.inner).filter_params()
    }

    // --- Distortion -------------------------------------------------

    /// Enable a waveshaping distortion on this bus. `drive` is the pre-gain
    /// into the saturator, `tone` a low-pass cutoff (Hz) on the shaped signal,
    /// `wet`/`dry` the mix levels.
    #[pyo3(signature = (drive = 4.0, tone = 8000.0, wet = 0.5, dry = 0.5))]
    fn enable_distortion(&mut self, drive: f32, tone: f32, wet: f32, dry: f32) -> PyResult<()> {
        lock(&self.inner)
            .enable_distortion(drive, tone, wet, dry)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to enable distortion: {:?}", e)))
    }

    fn disable_distortion(&mut self) { lock(&self.inner).disable_distortion(); }

    #[getter]
    fn has_distortion(&self) -> bool { lock(&self.inner).has_distortion() }

    fn set_distortion_params(&mut self, drive: f32, tone: f32, wet: f32, dry: f32) {
        lock(&self.inner).set_distortion_params(drive, tone, wet, dry);
    }

    /// (drive, tone, wet, dry) or None if distortion isn't enabled.
    #[getter]
    fn distortion_params(&self) -> Option<(f32, f32, f32, f32)> {
        lock(&self.inner).distortion_params()
    }

    // --- Vocoder ----------------------------------------------------

    /// Enable a single-input channel vocoder on this bus. The bus audio is the
    /// modulator; an internal carrier (0=sawtooth 1=pulse 2=noise) is shaped by
    /// its per-band envelope. `bands` is the band count (4-32), `carrier_freq`
    /// the carrier pitch (Hz) for tonal carriers, `attack`/`release` the
    /// envelope follower times (ms), `wet`/`dry` the mix.
    #[pyo3(signature = (bands = 16, carrier = 0, carrier_freq = 110.0, attack = 5.0, release = 60.0, wet = 1.0, dry = 0.0, rand_on = false, rand_rate = 6.0, rand_depth = 1.0, formant = 1.0, spread = 0.0, sibilance = 0.0))]
    fn enable_vocoder(&mut self, bands: i32, carrier: i32, carrier_freq: f32, attack: f32, release: f32, wet: f32, dry: f32,
                      rand_on: bool, rand_rate: f32, rand_depth: f32, formant: f32, spread: f32, sibilance: f32) -> PyResult<()> {
        lock(&self.inner)
            .enable_vocoder(bands, carrier, carrier_freq, attack, release, wet, dry,
                            rand_on, rand_rate, rand_depth, formant, spread, sibilance)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to enable vocoder: {:?}", e)))
    }

    fn disable_vocoder(&mut self) { lock(&self.inner).disable_vocoder(); }

    #[getter]
    fn has_vocoder(&self) -> bool { lock(&self.inner).has_vocoder() }

    fn set_vocoder_params(&mut self, bands: i32, carrier: i32, carrier_freq: f32, attack: f32, release: f32, wet: f32, dry: f32,
                          rand_on: bool, rand_rate: f32, rand_depth: f32, formant: f32, spread: f32, sibilance: f32) {
        lock(&self.inner).set_vocoder_params(bands, carrier, carrier_freq, attack, release, wet, dry,
                                                   rand_on, rand_rate, rand_depth, formant, spread, sibilance);
    }

    /// (bands, carrier, carrier_freq, attack, release, wet, dry) or None.
    #[getter]
    fn vocoder_params(&self) -> Option<(i32, i32, f32, f32, f32, f32, f32)> {
        lock(&self.inner).vocoder_params()
    }

    /// (rand_on, rand_rate, rand_depth, formant, spread, sibilance) or None.
    #[getter]
    fn vocoder_adv_params(&self) -> Option<(bool, f32, f32, f32, f32, f32)> {
        lock(&self.inner).vocoder_adv_params()
    }

    // --- Delay / echo -----------------------------------------------

    /// Enable a feedback delay / echo on this bus. `delay_ms` is the tap time,
    /// `feedback` the echo regeneration (0-0.95), `wet`/`dry` the mix levels.
    #[pyo3(signature = (delay_ms = 300.0, feedback = 0.35, wet = 0.35, dry = 1.0))]
    fn enable_delay(&mut self, delay_ms: f32, feedback: f32, wet: f32, dry: f32) -> PyResult<()> {
        lock(&self.inner)
            .enable_delay(delay_ms, feedback, wet, dry)
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to enable delay: {:?}", e)))
    }

    fn disable_delay(&mut self) { lock(&self.inner).disable_delay(); }

    #[getter]
    fn has_delay(&self) -> bool { lock(&self.inner).has_delay() }

    fn set_delay_params(&mut self, delay_ms: f32, feedback: f32, wet: f32, dry: f32) {
        lock(&self.inner).set_delay_params(delay_ms, feedback, wet, dry);
    }

    /// (delay_ms, feedback, wet, dry) or None if delay isn't enabled.
    #[getter]
    fn delay_params(&self) -> Option<(f32, f32, f32, f32)> {
        lock(&self.inner).delay_params()
    }
}

/// Manages audio playback and the 3D listener position.
#[pyclass]
struct SoundManager {
    inner: Arc<Mutex<RustSoundManager>>,
}

#[pymethods]
impl SoundManager {
    /// Create a new sound manager.
    #[new]
    fn new() -> PyResult<Self> {
        match RustSoundManager::new() {
            Ok(manager) => Ok(Self {
                inner: Arc::new(Mutex::new(manager)),
            }),
            Err(e) => Err(PyRuntimeError::new_err(format!(
                "Failed to create sound manager: {:?}",
                e
            ))),
        }
    }

    /// Create a new sound attached to this manager. If `group` is given, the
    /// sound feeds into that bus instead of the engine endpoint.
    #[pyo3(signature = (group = None))]
    fn create_sound(&mut self, group: Option<&SoundGroup>) -> PyResult<Sound> {
        let group_ref = group.map(|g| g.inner.clone());
        let sound = lock(&self.inner).create_sound_in_group(group_ref);
        Ok(Sound { inner: sound })
    }

    /// Create a new sound bus. Pass `parent=None` for a root bus that feeds the
    /// engine endpoint, or another SoundGroup to nest buses.
    #[pyo3(signature = (parent = None))]
    fn create_group(&mut self, parent: Option<&SoundGroup>) -> PyResult<SoundGroup> {
        let parent_ref = parent.map(|g| g.inner.clone());
        match lock(&self.inner).create_group(parent_ref) {
            Ok(group) => Ok(SoundGroup { inner: group }),
            Err(e) => Err(PyRuntimeError::new_err(format!("Failed to create group: {:?}", e))),
        }
    }

    /// Set the 3D listener position.
    fn set_listener_position(&mut self, x: f32, y: f32, z: f32) {
        lock(&self.inner).set_listener_position(x, y, z);
    }

    /// Set the listener facing angle.
    fn set_listener_angle(&mut self, angle: f32) {
        lock(&self.inner).set_listener_angle(angle);
    }

    /// Set both listener position and angle at once.
    fn set_listener(&mut self, x: f32, y: f32, z: f32, angle: f32) {
        lock(&self.inner).set_listener(x, y, z, angle);
    }

    /// Advance per-sound automation (pitch tweens) and refresh spatialization.
    ///
    /// Listener updates already trigger this. Call manually if you have active
    /// tweens but the listener isn't moving this frame.
    fn tick(&mut self) {
        lock(&self.inner).tick();
    }

    /// Get the listener facing angle.
    #[getter]
    fn listener_angle(&self) -> f32 {
        lock(&self.inner).listener_angle()
    }

    /// Check if HRTF is available.
    #[getter]
    fn hrtf_available(&self) -> bool {
        lock(&self.inner).is_hrtf_available()
    }

    /// Destroy the sound manager (no-op, resources cleaned up on drop).
    fn destroy(&self) {
        // Resources are automatically cleaned up when the object is dropped
    }
}

/// Interface for text-to-speech through the system screen reader.
// `unsendable` like the other audio classes: the inner driver holds a
// non-Sync `Box<dyn ScreenReaderDriver>`, and pyo3 0.23+ requires pyclasses to
// be Send + Sync unless opted out. It's tied to the thread that created it.
#[pyclass(unsendable)]
struct ScreenReader {
    inner: RustScreenReader,
}

#[pymethods]
impl ScreenReader {
    /// Create a new screen reader interface.
    #[new]
    fn new() -> PyResult<Self> {
        Ok(Self {
            inner: RustScreenReader::new(),
        })
    }

    /// Check if the screen reader is available and can speak.
    #[getter]
    fn can_speak(&self) -> bool {
        self.inner.can_speak()
    }

    /// Speak the given text.
    fn speak(&mut self, text: &str) -> PyResult<()> {
        self.inner
            .speak(text)
            .map_err(|e| PyRuntimeError::new_err(format!("{}", e)))
    }

    /// Stop any current speech.
    fn stop(&mut self) -> PyResult<()> {
        self.inner
            .stop()
            .map_err(|e| PyRuntimeError::new_err(format!("{}", e)))
    }

    /// Check if currently speaking.
    #[getter]
    fn is_speaking(&self) -> bool {
        self.inner.is_speaking().unwrap_or(false)
    }
}

/// A window for receiving keyboard input.
#[pyclass(unsendable)]
struct Window {
    inner: RustWindow,
}

#[pymethods]
impl Window {
    /// Create a new window with the given title.
    #[new]
    #[pyo3(signature = (title = "Cosmos"))]
    fn new(title: &str) -> PyResult<Self> {
        match RustWindow::new(title) {
            Ok(window) => Ok(Self { inner: window }),
            Err(e) => Err(PyRuntimeError::new_err(format!(
                "Failed to create window: {}",
                e
            ))),
        }
    }

    /// Check if the window is still open.
    #[getter]
    fn is_open(&self) -> bool {
        self.inner.is_open()
    }

    /// Close the window.
    fn close(&mut self) {
        self.inner.close();
    }

    /// Destroy the window and release resources.
    fn destroy(&mut self) {
        self.inner.destroy();
    }

    /// Update the window and process events.
    fn update(&mut self) {
        self.inner.update();
    }

    /// Check if a key was pressed this frame.
    fn key_pressed(&self, key: i32) -> bool {
        self.inner.key_pressed_raw(key)
    }

    /// Check if a key is being held down.
    fn key_held(&self, key: i32) -> bool {
        self.inner.key_held_raw(key)
    }

    /// Check if a key was released this frame.
    fn key_released(&self, key: i32) -> bool {
        self.inner.key_released_raw(key)
    }
}

/// Key constants module
#[pyclass]
#[allow(non_snake_case)]
struct Key;

#[pymethods]
#[allow(non_snake_case)]
impl Key {
    // Letters
    #[classattr] fn A() -> i32 { RustKey::A as i32 }
    #[classattr] fn B() -> i32 { RustKey::B as i32 }
    #[classattr] fn C() -> i32 { RustKey::C as i32 }
    #[classattr] fn D() -> i32 { RustKey::D as i32 }
    #[classattr] fn E() -> i32 { RustKey::E as i32 }
    #[classattr] fn F() -> i32 { RustKey::F as i32 }
    #[classattr] fn G() -> i32 { RustKey::G as i32 }
    #[classattr] fn H() -> i32 { RustKey::H as i32 }
    #[classattr] fn I() -> i32 { RustKey::I as i32 }
    #[classattr] fn J() -> i32 { RustKey::J as i32 }
    #[classattr] fn K() -> i32 { RustKey::K as i32 }
    #[classattr] fn L() -> i32 { RustKey::L as i32 }
    #[classattr] fn M() -> i32 { RustKey::M as i32 }
    #[classattr] fn N() -> i32 { RustKey::N as i32 }
    #[classattr] fn O() -> i32 { RustKey::O as i32 }
    #[classattr] fn P() -> i32 { RustKey::P as i32 }
    #[classattr] fn Q() -> i32 { RustKey::Q as i32 }
    #[classattr] fn R() -> i32 { RustKey::R as i32 }
    #[classattr] fn S() -> i32 { RustKey::S as i32 }
    #[classattr] fn T() -> i32 { RustKey::T as i32 }
    #[classattr] fn U() -> i32 { RustKey::U as i32 }
    #[classattr] fn V() -> i32 { RustKey::V as i32 }
    #[classattr] fn W() -> i32 { RustKey::W as i32 }
    #[classattr] fn X() -> i32 { RustKey::X as i32 }
    #[classattr] fn Y() -> i32 { RustKey::Y as i32 }
    #[classattr] fn Z() -> i32 { RustKey::Z as i32 }

    // Numbers
    #[classattr] fn N0() -> i32 { RustKey::N0 as i32 }
    #[classattr] fn N1() -> i32 { RustKey::N1 as i32 }
    #[classattr] fn N2() -> i32 { RustKey::N2 as i32 }
    #[classattr] fn N3() -> i32 { RustKey::N3 as i32 }
    #[classattr] fn N4() -> i32 { RustKey::N4 as i32 }
    #[classattr] fn N5() -> i32 { RustKey::N5 as i32 }
    #[classattr] fn N6() -> i32 { RustKey::N6 as i32 }
    #[classattr] fn N7() -> i32 { RustKey::N7 as i32 }
    #[classattr] fn N8() -> i32 { RustKey::N8 as i32 }
    #[classattr] fn N9() -> i32 { RustKey::N9 as i32 }

    // Function keys
    #[classattr] fn F1() -> i32 { RustKey::F1 as i32 }
    #[classattr] fn F2() -> i32 { RustKey::F2 as i32 }
    #[classattr] fn F3() -> i32 { RustKey::F3 as i32 }
    #[classattr] fn F4() -> i32 { RustKey::F4 as i32 }
    #[classattr] fn F5() -> i32 { RustKey::F5 as i32 }
    #[classattr] fn F6() -> i32 { RustKey::F6 as i32 }
    #[classattr] fn F7() -> i32 { RustKey::F7 as i32 }
    #[classattr] fn F8() -> i32 { RustKey::F8 as i32 }
    #[classattr] fn F9() -> i32 { RustKey::F9 as i32 }
    #[classattr] fn F10() -> i32 { RustKey::F10 as i32 }
    #[classattr] fn F11() -> i32 { RustKey::F11 as i32 }
    #[classattr] fn F12() -> i32 { RustKey::F12 as i32 }

    // Special keys
    #[classattr] fn SPACE() -> i32 { RustKey::Space as i32 }
    #[classattr] fn ESCAPE() -> i32 { RustKey::Escape as i32 }
    #[classattr] fn ENTER() -> i32 { RustKey::Enter as i32 }
    #[classattr] fn TAB() -> i32 { RustKey::Tab as i32 }
    #[classattr] fn BACKSPACE() -> i32 { RustKey::Backspace as i32 }

    // Arrow keys
    #[classattr] fn UP() -> i32 { RustKey::Up as i32 }
    #[classattr] fn DOWN() -> i32 { RustKey::Down as i32 }
    #[classattr] fn LEFT() -> i32 { RustKey::Left as i32 }
    #[classattr] fn RIGHT() -> i32 { RustKey::Right as i32 }

    // Modifiers
    #[classattr] fn LSHIFT() -> i32 { RustKey::LShift as i32 }
    #[classattr] fn RSHIFT() -> i32 { RustKey::RShift as i32 }
    #[classattr] fn LCTRL() -> i32 { RustKey::LCtrl as i32 }
    #[classattr] fn RCTRL() -> i32 { RustKey::RCtrl as i32 }
    #[classattr] fn LALT() -> i32 { RustKey::LAlt as i32 }
    #[classattr] fn RALT() -> i32 { RustKey::RAlt as i32 }

    // Navigation
    #[classattr] fn INSERT() -> i32 { RustKey::Insert as i32 }
    #[classattr] fn DELETE() -> i32 { RustKey::Delete as i32 }
    #[classattr] fn HOME() -> i32 { RustKey::Home as i32 }
    #[classattr] fn END() -> i32 { RustKey::End as i32 }
    #[classattr] fn PAGEUP() -> i32 { RustKey::PageUp as i32 }
    #[classattr] fn PAGEDOWN() -> i32 { RustKey::PageDown as i32 }

    // Punctuation
    #[classattr] fn MINUS() -> i32 { RustKey::Minus as i32 }
    #[classattr] fn EQUALS() -> i32 { RustKey::Equals as i32 }
    #[classattr] fn LEFTBRACKET() -> i32 { RustKey::LeftBracket as i32 }
    #[classattr] fn RIGHTBRACKET() -> i32 { RustKey::RightBracket as i32 }
    #[classattr] fn BACKSLASH() -> i32 { RustKey::Backslash as i32 }
    #[classattr] fn SEMICOLON() -> i32 { RustKey::Semicolon as i32 }
    #[classattr] fn APOSTROPHE() -> i32 { RustKey::Apostrophe as i32 }
    #[classattr] fn GRAVE() -> i32 { RustKey::Grave as i32 }
    #[classattr] fn COMMA() -> i32 { RustKey::Comma as i32 }
    #[classattr] fn PERIOD() -> i32 { RustKey::Period as i32 }
    #[classattr] fn SLASH() -> i32 { RustKey::Slash as i32 }

    // Numpad
    #[classattr] fn KP0() -> i32 { RustKey::Kp0 as i32 }
    #[classattr] fn KP1() -> i32 { RustKey::Kp1 as i32 }
    #[classattr] fn KP2() -> i32 { RustKey::Kp2 as i32 }
    #[classattr] fn KP3() -> i32 { RustKey::Kp3 as i32 }
    #[classattr] fn KP4() -> i32 { RustKey::Kp4 as i32 }
    #[classattr] fn KP5() -> i32 { RustKey::Kp5 as i32 }
    #[classattr] fn KP6() -> i32 { RustKey::Kp6 as i32 }
    #[classattr] fn KP7() -> i32 { RustKey::Kp7 as i32 }
    #[classattr] fn KP8() -> i32 { RustKey::Kp8 as i32 }
    #[classattr] fn KP9() -> i32 { RustKey::Kp9 as i32 }
    #[classattr] fn KP_ENTER() -> i32 { RustKey::KpEnter as i32 }
    #[classattr] fn KP_PLUS() -> i32 { RustKey::KpPlus as i32 }
    #[classattr] fn KP_MINUS() -> i32 { RustKey::KpMinus as i32 }
    #[classattr] fn KP_MULTIPLY() -> i32 { RustKey::KpMultiply as i32 }
    #[classattr] fn KP_DIVIDE() -> i32 { RustKey::KpDivide as i32 }
    #[classattr] fn KP_PERIOD() -> i32 { RustKey::KpPeriod as i32 }
}

/// Cosmos audio game library for Python.
#[pymodule]
fn cosmos(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SoundManager>()?;
    m.add_class::<SoundGroup>()?;
    m.add_class::<Sound>()?;
    m.add_class::<ScreenReader>()?;
    m.add_class::<Window>()?;
    m.add_class::<Key>()?;
    Ok(())
}
