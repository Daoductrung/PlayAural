//! Sound groups / buses — graph nodes that apply volume/pitch to attached sounds.
//!
//! A `SoundGroup` is a `ma_sound_group` (miniaudio typedefs this as `ma_sound`).
//! Sounds and other groups can attach to a group's input, and the group feeds
//! either the engine endpoint or another parent group. Use them to mix whole
//! categories of audio — e.g. a `weapons` bus, or a `master` bus that slow-mo
//! can pitch-tween all at once.

use miniaudio_sys::{
    ma_node, ma_node_attach_output_bus, ma_node_detach_output_bus, ma_sound, ma_sound_alloc,
    ma_sound_free, ma_sound_group_init, ma_sound_group_uninit, ma_sound_set_pitch,
    ma_sound_set_volume, ma_sound_start, ma_sound_stop, MA_SUCCESS,
};
use std::ptr;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

use crate::delay::DelayNode;
use crate::disperser::DisperserNode;
use crate::distortion::DistortionNode;
use crate::engine::AudioEngine;
use crate::eq::EqNode;
use crate::error::AudioError;
use crate::filter::FilterNode;
use crate::reverb::ReverbNode;
use crate::tween::{Easing, PitchTween};
use crate::sync::lock;
use crate::vocoder::VocoderNode;

// Pull in the miniaudio helper from miniaudio_impl.c — same one sound.rs
// declares locally. ma_sound_group is typedef'd to ma_sound so this covers
// both.
extern "C" {
    fn ma_sound_get_node_ptr(sound: *mut ma_sound) -> *mut ma_node;
}

/// Reference-counted handle to a sound group. Kept by the SoundManager so
/// groups can be ticked each frame, and by Sounds that route through them.
pub type SoundGroupRef = Arc<Mutex<SoundGroup>>;

/// A miniaudio sound group (bus). Applies volume/pitch to everything attached.
///
/// Groups form a tree rooted at the engine's endpoint. Create via
/// `SoundManager::create_group()` (default parent = endpoint) or nest them
/// by passing a parent group.
pub struct SoundGroup {
    group: *mut ma_sound,
    initialized: bool,
    engine: Arc<Mutex<AudioEngine>>,

    base_volume: f32,
    base_pitch: f32,
    pitch_tween: Option<PitchTween>,

    // Effect chain nodes. When any subset is enabled, the audio routes
    // group -> filter -> eq -> distortion -> vocoder -> disperser -> delay ->
    // reverb -> downstream (in that fixed order, skipping any disabled slot).
    // `rebuild_effect_chain()` wires it all up.
    filter: Option<FilterNode>,
    eq: Option<EqNode>,
    distortion: Option<DistortionNode>,
    vocoder: Option<VocoderNode>,
    disperser: Option<DisperserNode>,
    delay: Option<DelayNode>,
    reverb: Option<ReverbNode>,

    // Keep parent alive while we're attached to it, and for introspection.
    _parent: Option<SoundGroupRef>,
}

impl SoundGroup {
    pub(crate) fn new(
        engine: Arc<Mutex<AudioEngine>>,
        parent: Option<SoundGroupRef>,
    ) -> Result<Self, AudioError> {
        let group = unsafe { ma_sound_alloc() };
        if group.is_null() {
            return Err(AudioError::AllocationFailed);
        }

        let engine_ptr = lock(&engine).as_ptr();
        let parent_ptr: *mut ma_sound = parent
            .as_ref()
            .map_or(ptr::null_mut(), |p| lock(p).group);

        let result = unsafe { ma_sound_group_init(engine_ptr, 0, parent_ptr, group) };
        if result != MA_SUCCESS {
            unsafe { ma_sound_free(group) };
            return Err(AudioError::AllocationFailed);
        }

        Ok(Self {
            group,
            initialized: true,
            engine,
            base_volume: 1.0,
            base_pitch: 1.0,
            pitch_tween: None,
            filter: None,
            eq: None,
            distortion: None,
            vocoder: None,
            disperser: None,
            delay: None,
            reverb: None,
            _parent: parent,
        })
    }

    /// The node this group currently feeds into (parent bus or engine endpoint).
    /// Used when (re)wiring the effect chain between the group and its parent.
    fn downstream_node_ptr(&self) -> *mut ma_node {
        if let Some(p) = self._parent.as_ref() {
            lock(p).as_ptr() as *mut ma_node
        } else {
            lock(&self.engine).get_endpoint() as *mut ma_node
        }
    }

    /// Rebuild the effect chain. Detaches every effect node (and the group
    /// itself) from its current output, then re-wires in fixed order:
    /// `group → eq → disperser → reverb → downstream`, skipping any
    /// disabled slot. Call after toggling any effect.
    fn rebuild_effect_chain(&mut self) {
        let downstream = self.downstream_node_ptr();
        let group_node = unsafe { ma_sound_get_node_ptr(self.group) };
        if group_node.is_null() {
            return;
        }

        // Collect enabled effect node ptrs in chain order:
        // filter -> eq -> distortion -> vocoder -> disperser -> delay -> reverb.
        let mut chain: Vec<*mut ma_node> = Vec::with_capacity(7);
        if let Some(f) = self.filter.as_ref()     { chain.push(f.as_ma_node()); }
        if let Some(e) = self.eq.as_ref()         { chain.push(e.as_ma_node()); }
        if let Some(x) = self.distortion.as_ref() { chain.push(x.as_ma_node()); }
        if let Some(v) = self.vocoder.as_ref()    { chain.push(v.as_ma_node()); }
        if let Some(d) = self.disperser.as_ref()  { chain.push(d.as_ma_node()); }
        if let Some(l) = self.delay.as_ref()      { chain.push(l.as_ma_node()); }
        if let Some(r) = self.reverb.as_ref()     { chain.push(r.as_ma_node()); }

        unsafe {
            ma_node_detach_output_bus(group_node, 0);
            for &n in &chain {
                ma_node_detach_output_bus(n, 0);
            }

            let mut prev = group_node;
            for &n in &chain {
                ma_node_attach_output_bus(prev, 0, n, 0);
                prev = n;
            }
            ma_node_attach_output_bus(prev, 0, downstream, 0);
        }
    }

    // ---------- Reverb --------------------------------------------------

    #[allow(clippy::too_many_arguments)]
    pub fn enable_reverb(
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
    ) -> Result<(), AudioError> {
        if self.reverb.is_none() {
            let graph = lock(&self.engine).get_node_graph();
            let sr = lock(&self.engine).sample_rate();
            self.reverb = Some(ReverbNode::new(graph, sr)?);
            self.rebuild_effect_chain();
        }
        if let Some(rv) = self.reverb.as_mut() {
            rv.set_wet(wet);
            rv.set_dry(dry);
            rv.set_predelay(predelay);
            rv.set_ir_gain(ir_gain);
            rv.set_width(width);
            rv.set_lowcut(lowcut);
            rv.set_highcut(highcut);
            rv.set_diffuse(diffuse);
            // Decay reshapes the IR (a partition rebuild) — only do it when the
            // value actually changed so live tweaks of the cheap params don't
            // trigger a rebuild + tail reset on every keystroke.
            if (rv.decay() - decay).abs() > 1e-4 {
                rv.set_decay(decay);
            }
        }
        Ok(())
    }

    pub fn disable_reverb(&mut self) {
        if self.reverb.is_none() { return; }
        self.reverb = None;
        self.rebuild_effect_chain();
    }

    pub fn has_reverb(&self) -> bool { self.reverb.is_some() }

    #[allow(clippy::too_many_arguments)]
    pub fn set_reverb_params(&mut self, wet: f32, dry: f32, predelay: f32, ir_gain: f32,
                             width: f32, decay: f32, lowcut: f32, highcut: f32, diffuse: f32) {
        if let Some(rv) = self.reverb.as_mut() {
            rv.set_wet(wet);
            rv.set_dry(dry);
            rv.set_predelay(predelay);
            rv.set_ir_gain(ir_gain);
            rv.set_width(width);
            rv.set_lowcut(lowcut);
            rv.set_highcut(highcut);
            rv.set_diffuse(diffuse);
            // Only rebuild if the decay actually changed — avoids a needless
            // partition rebuild on every live slider tweak of the other params.
            if (rv.decay() - decay).abs() > 1e-4 {
                rv.set_decay(decay);
            }
        }
    }

    pub fn reverb_params(&self) -> Option<(f32, f32, f32, f32, f32, f32, f32, f32, f32)> {
        self.reverb.as_ref().map(|rv| {
            (rv.wet(), rv.dry(), rv.predelay(), rv.ir_gain(),
             rv.width(), rv.decay(), rv.lowcut(), rv.highcut(), rv.diffuse())
        })
    }

    /// Load a custom impulse response onto the reverb (no-op if reverb isn't
    /// enabled). Returns true on success.
    pub fn set_reverb_ir(&mut self, path: &str) -> bool {
        if let Some(rv) = self.reverb.as_mut() {
            rv.load_ir(path).is_ok()
        } else {
            false
        }
    }

    /// Restore the built-in synthetic IR. Returns true on success.
    pub fn reset_reverb_ir(&mut self) -> bool {
        if let Some(rv) = self.reverb.as_mut() {
            rv.load_default_ir().is_ok()
        } else {
            false
        }
    }

    // ---------- EQ ------------------------------------------------------

    pub fn enable_eq(
        &mut self,
        low_gain: f32, mid_gain: f32, high_gain: f32,
        low_freq: f32, mid_freq: f32, high_freq: f32, mid_q: f32,
    ) -> Result<(), AudioError> {
        if self.eq.is_none() {
            let graph = lock(&self.engine).get_node_graph();
            let sr = lock(&self.engine).sample_rate();
            self.eq = Some(EqNode::new(graph, sr)?);
            self.rebuild_effect_chain();
        }
        if let Some(eq) = self.eq.as_mut() {
            eq.set_low_freq(low_freq);
            eq.set_mid_freq(mid_freq);
            eq.set_high_freq(high_freq);
            eq.set_low_gain(low_gain);
            eq.set_mid_gain(mid_gain);
            eq.set_high_gain(high_gain);
            eq.set_mid_q(mid_q);
        }
        Ok(())
    }

    pub fn disable_eq(&mut self) {
        if self.eq.is_none() { return; }
        self.eq = None;
        self.rebuild_effect_chain();
    }

    pub fn has_eq(&self) -> bool { self.eq.is_some() }

    pub fn set_eq_params(
        &mut self,
        low_gain: f32, mid_gain: f32, high_gain: f32,
        low_freq: f32, mid_freq: f32, high_freq: f32, mid_q: f32,
    ) {
        if let Some(eq) = self.eq.as_mut() {
            eq.set_low_freq(low_freq);
            eq.set_mid_freq(mid_freq);
            eq.set_high_freq(high_freq);
            eq.set_low_gain(low_gain);
            eq.set_mid_gain(mid_gain);
            eq.set_high_gain(high_gain);
            eq.set_mid_q(mid_q);
        }
    }

    /// (low_gain_db, mid_gain_db, high_gain_db, low_freq, mid_freq, high_freq, mid_q)
    pub fn eq_params(&self) -> Option<(f32, f32, f32, f32, f32, f32, f32)> {
        self.eq.as_ref().map(|eq| {
            (eq.low_gain(), eq.mid_gain(), eq.high_gain(),
             eq.low_freq(), eq.mid_freq(), eq.high_freq(), eq.mid_q())
        })
    }

    // ---------- Disperser ----------------------------------------------

    pub fn enable_disperser(
        &mut self,
        freq: f32,
        q: f32,
        stages: i32,
    ) -> Result<(), AudioError> {
        if self.disperser.is_none() {
            let graph = lock(&self.engine).get_node_graph();
            let sr = lock(&self.engine).sample_rate();
            self.disperser = Some(DisperserNode::new(graph, sr)?);
            self.rebuild_effect_chain();
        }
        if let Some(d) = self.disperser.as_mut() {
            d.set_freq(freq);
            d.set_q(q);
            d.set_stages(stages);
        }
        Ok(())
    }

    pub fn disable_disperser(&mut self) {
        if self.disperser.is_none() { return; }
        self.disperser = None;
        self.rebuild_effect_chain();
    }

    pub fn has_disperser(&self) -> bool { self.disperser.is_some() }

    pub fn set_disperser_params(&mut self, freq: f32, q: f32, stages: i32) {
        if let Some(d) = self.disperser.as_mut() {
            d.set_freq(freq);
            d.set_q(q);
            d.set_stages(stages);
        }
    }

    /// (freq, q, stages)
    pub fn disperser_params(&self) -> Option<(f32, f32, i32)> {
        self.disperser.as_ref().map(|d| (d.freq(), d.q(), d.stages()))
    }

    // ---------- Filter (multimode biquad) -------------------------------

    pub fn enable_filter(&mut self, mode: i32, freq: f32, q: f32, gain: f32) -> Result<(), AudioError> {
        if self.filter.is_none() {
            let graph = lock(&self.engine).get_node_graph();
            let sr = lock(&self.engine).sample_rate();
            self.filter = Some(FilterNode::new(graph, sr)?);
            self.rebuild_effect_chain();
        }
        if let Some(f) = self.filter.as_mut() {
            f.set_mode(mode);
            f.set_freq(freq);
            f.set_q(q);
            f.set_gain(gain);
        }
        Ok(())
    }

    pub fn disable_filter(&mut self) {
        if self.filter.is_none() { return; }
        self.filter = None;
        self.rebuild_effect_chain();
    }

    pub fn has_filter(&self) -> bool { self.filter.is_some() }

    pub fn set_filter_params(&mut self, mode: i32, freq: f32, q: f32, gain: f32) {
        if let Some(f) = self.filter.as_mut() {
            f.set_mode(mode);
            f.set_freq(freq);
            f.set_q(q);
            f.set_gain(gain);
        }
    }

    /// (mode, freq, q, gain)
    pub fn filter_params(&self) -> Option<(i32, f32, f32, f32)> {
        self.filter.as_ref().map(|f| (f.mode(), f.freq(), f.q(), f.gain()))
    }

    // ---------- Distortion ----------------------------------------------

    pub fn enable_distortion(&mut self, drive: f32, tone: f32, wet: f32, dry: f32) -> Result<(), AudioError> {
        if self.distortion.is_none() {
            let graph = lock(&self.engine).get_node_graph();
            let sr = lock(&self.engine).sample_rate();
            self.distortion = Some(DistortionNode::new(graph, sr)?);
            self.rebuild_effect_chain();
        }
        if let Some(d) = self.distortion.as_mut() {
            d.set_drive(drive);
            d.set_tone(tone);
            d.set_wet(wet);
            d.set_dry(dry);
        }
        Ok(())
    }

    pub fn disable_distortion(&mut self) {
        if self.distortion.is_none() { return; }
        self.distortion = None;
        self.rebuild_effect_chain();
    }

    pub fn has_distortion(&self) -> bool { self.distortion.is_some() }

    pub fn set_distortion_params(&mut self, drive: f32, tone: f32, wet: f32, dry: f32) {
        if let Some(d) = self.distortion.as_mut() {
            d.set_drive(drive);
            d.set_tone(tone);
            d.set_wet(wet);
            d.set_dry(dry);
        }
    }

    /// (drive, tone, wet, dry)
    pub fn distortion_params(&self) -> Option<(f32, f32, f32, f32)> {
        self.distortion.as_ref().map(|d| (d.drive(), d.tone(), d.wet(), d.dry()))
    }

    // ---------- Vocoder -------------------------------------------------

    #[allow(clippy::too_many_arguments)]
    pub fn enable_vocoder(
        &mut self,
        bands: i32, carrier: i32, carrier_freq: f32,
        attack: f32, release: f32, wet: f32, dry: f32,
        rand_on: bool, rand_rate: f32, rand_depth: f32,
        formant: f32, spread: f32, sibilance: f32,
    ) -> Result<(), AudioError> {
        if self.vocoder.is_none() {
            let graph = lock(&self.engine).get_node_graph();
            let sr = lock(&self.engine).sample_rate();
            self.vocoder = Some(VocoderNode::new(graph, sr)?);
            self.rebuild_effect_chain();
        }
        self.set_vocoder_params(
            bands, carrier, carrier_freq, attack, release, wet, dry,
            rand_on, rand_rate, rand_depth, formant, spread, sibilance);
        Ok(())
    }

    pub fn disable_vocoder(&mut self) {
        if self.vocoder.is_none() { return; }
        self.vocoder = None;
        self.rebuild_effect_chain();
    }

    pub fn has_vocoder(&self) -> bool { self.vocoder.is_some() }

    #[allow(clippy::too_many_arguments)]
    pub fn set_vocoder_params(
        &mut self,
        bands: i32, carrier: i32, carrier_freq: f32,
        attack: f32, release: f32, wet: f32, dry: f32,
        rand_on: bool, rand_rate: f32, rand_depth: f32,
        formant: f32, spread: f32, sibilance: f32,
    ) {
        if let Some(v) = self.vocoder.as_mut() {
            v.set_bands(bands);
            v.set_carrier(carrier);
            v.set_carrier_freq(carrier_freq);
            v.set_attack(attack);
            v.set_release(release);
            v.set_wet(wet);
            v.set_dry(dry);
            v.set_rand(rand_on);
            v.set_rand_rate(rand_rate);
            v.set_rand_depth(rand_depth);
            v.set_formant(formant);
            v.set_spread(spread);
            v.set_sibilance(sibilance);
        }
    }

    /// (bands, carrier, carrier_freq, attack, release, wet, dry)
    pub fn vocoder_params(&self) -> Option<(i32, i32, f32, f32, f32, f32, f32)> {
        self.vocoder.as_ref().map(|v| {
            (v.bands(), v.carrier(), v.carrier_freq(), v.attack(), v.release(), v.wet(), v.dry())
        })
    }

    /// (rand_on, rand_rate, rand_depth, formant, spread, sibilance)
    pub fn vocoder_adv_params(&self) -> Option<(bool, f32, f32, f32, f32, f32)> {
        self.vocoder.as_ref().map(|v| {
            (v.rand_on(), v.rand_rate(), v.rand_depth(), v.formant(), v.spread(), v.sibilance())
        })
    }

    // ---------- Delay / echo --------------------------------------------

    pub fn enable_delay(&mut self, delay_ms: f32, feedback: f32, wet: f32, dry: f32) -> Result<(), AudioError> {
        if self.delay.is_none() {
            let graph = lock(&self.engine).get_node_graph();
            let sr = lock(&self.engine).sample_rate();
            self.delay = Some(DelayNode::new(graph, sr)?);
            self.rebuild_effect_chain();
        }
        if let Some(l) = self.delay.as_mut() {
            l.set_delay_ms(delay_ms);
            l.set_feedback(feedback);
            l.set_wet(wet);
            l.set_dry(dry);
        }
        Ok(())
    }

    pub fn disable_delay(&mut self) {
        if self.delay.is_none() { return; }
        self.delay = None;
        self.rebuild_effect_chain();
    }

    pub fn has_delay(&self) -> bool { self.delay.is_some() }

    pub fn set_delay_params(&mut self, delay_ms: f32, feedback: f32, wet: f32, dry: f32) {
        if let Some(l) = self.delay.as_mut() {
            l.set_delay_ms(delay_ms);
            l.set_feedback(feedback);
            l.set_wet(wet);
            l.set_dry(dry);
        }
    }

    /// (delay_ms, feedback, wet, dry)
    pub fn delay_params(&self) -> Option<(f32, f32, f32, f32)> {
        self.delay.as_ref().map(|l| (l.delay_ms(), l.feedback(), l.wet(), l.dry()))
    }

    /// Raw group pointer for attaching sounds / nested groups.
    pub(crate) fn as_ptr(&self) -> *mut ma_sound {
        self.group
    }

    pub fn set_volume(&mut self, volume: f32) {
        self.base_volume = volume;
        if self.initialized {
            unsafe { ma_sound_set_volume(self.group, volume) };
        }
    }

    pub fn volume(&self) -> f32 {
        self.base_volume
    }

    /// Set pitch (1.0 = normal). Cancels any running pitch tween.
    pub fn set_pitch(&mut self, pitch: f32) {
        self.base_pitch = pitch;
        self.pitch_tween = None;
        if self.initialized {
            unsafe { ma_sound_set_pitch(self.group, pitch) };
        }
    }

    pub fn pitch(&self) -> f32 {
        self.base_pitch
    }

    /// Smoothly interpolate the bus pitch to `target` over `duration`.
    /// Replaces any existing tween. Advances on each `SoundManager::tick()`.
    pub fn tween_pitch(&mut self, target: f32, duration: Duration, easing: Easing) {
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
        self.advance_pitch_tween();
    }

    /// Cancel any active pitch tween. The bus pitch holds at its current value.
    pub fn stop_pitch_tween(&mut self) {
        if let Some(active) = &self.pitch_tween {
            let (current, _) = active.sample();
            self.base_pitch = current;
        }
        self.pitch_tween = None;
        if self.initialized {
            unsafe { ma_sound_set_pitch(self.group, self.base_pitch) };
        }
    }

    pub fn is_pitch_tweening(&self) -> bool {
        self.pitch_tween.is_some()
    }

    /// Start / stop / pause the whole bus.
    pub fn play(&mut self) {
        if self.initialized {
            unsafe { ma_sound_start(self.group) };
        }
    }

    pub fn stop(&mut self) {
        if self.initialized {
            unsafe { ma_sound_stop(self.group) };
        }
    }

    /// Advance any active pitch tween. Returns true if a tween was advanced.
    /// Called by SoundManager::tick().
    pub(crate) fn advance_pitch_tween(&mut self) -> bool {
        let (value, done) = match &self.pitch_tween {
            Some(tween) => tween.sample(),
            None => return false,
        };
        self.base_pitch = value;
        if self.initialized {
            unsafe { ma_sound_set_pitch(self.group, value) };
        }
        if done {
            self.pitch_tween = None;
        }
        true
    }
}

impl Drop for SoundGroup {
    fn drop(&mut self) {
        // Tear every effect out of the graph first so the group's own uninit
        // doesn't leave dangling edges.
        if self.filter.is_some() || self.eq.is_some() || self.distortion.is_some()
            || self.vocoder.is_some() || self.disperser.is_some() || self.delay.is_some()
            || self.reverb.is_some()
        {
            self.filter = None;
            self.eq = None;
            self.distortion = None;
            self.vocoder = None;
            self.disperser = None;
            self.delay = None;
            self.reverb = None;
            self.rebuild_effect_chain();
        }
        unsafe {
            if self.initialized {
                ma_sound_group_uninit(self.group);
            }
            if !self.group.is_null() {
                ma_sound_free(self.group);
            }
        }
    }
}

// SAFETY: a `SoundGroup` is only ever reached through the `Mutex` in its
// `SoundGroupRef`, so one caller thread at a time touches the group node and
// its effect nodes. Graph attach/detach and the effect parameter setters are
// designed by miniaudio to be driven from a control thread while the audio
// thread runs; which control thread does not matter.
unsafe impl Send for SoundGroup {}
