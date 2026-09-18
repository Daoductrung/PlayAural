//! Offline check of the COSMOS PATCHes to node start and stop times in
//! miniaudio.h: a sound scheduled to start k frames into a graph read must
//! begin at frame k, and one scheduled to stop there must fall silent at k.
//!
//! The engine runs with no device, so the test drives the node graph itself
//! with `ma_engine_read_pcm_frames` in periods of 512 frames and looks at
//! where sound arrives and where it ends. Upstream 0.11.23 defers a start
//! inside a read to the next read (100 lands at 512, 700 at 1024) and cuts
//! the whole read containing a stop (a stop at 700 ends at 512).

use miniaudio_sys::*;
use std::os::raw::c_void;

const PERIOD: usize = 512;
const RATE: u32 = 48_000;

/// Render `total_frames` of a mono engine holding one sound made from
/// `source`, started at `start_frame` and stopped at `stop_frame` if given.
fn render(source: &[f32], start_frame: u64, stop_frame: Option<u64>, total_frames: usize) -> Vec<f32> {
    unsafe {
        let engine = ma_engine_alloc();
        assert!(!engine.is_null(), "ma_engine_alloc");
        let mut engine_config = ma_engine_config_init();
        engine_config.noDevice = MA_TRUE;
        engine_config.channels = 1;
        engine_config.sampleRate = RATE;
        engine_config.periodSizeInFrames = PERIOD as ma_uint32;
        assert_eq!(ma_engine_init(&engine_config, engine), MA_SUCCESS, "ma_engine_init");

        let mut buffer: ma_audio_buffer = std::mem::zeroed();
        let mut buffer_config = ma_audio_buffer_config_init(
            ma_format_f32,
            1,
            source.len() as ma_uint64,
            source.as_ptr() as *const c_void,
            std::ptr::null(),
        );
        // The config leaves the rate at 0, which the engine node treats as
        // a rate mismatch and routes through the linear resampler, and that
        // delays everything by one frame.
        buffer_config.sampleRate = RATE;
        assert_eq!(
            ma_audio_buffer_init(&buffer_config, &mut buffer),
            MA_SUCCESS,
            "ma_audio_buffer_init"
        );

        let sound = ma_sound_alloc();
        assert!(!sound.is_null(), "ma_sound_alloc");
        // No pitch shifting and no spatialization: samples must reach the
        // output unchanged, at the frame they were read.
        assert_eq!(
            ma_sound_init_from_data_source(
                engine,
                &mut buffer as *mut ma_audio_buffer as *mut ma_data_source,
                MA_SOUND_FLAG_NO_PITCH | MA_SOUND_FLAG_NO_SPATIALIZATION,
                std::ptr::null_mut(),
                sound,
            ),
            MA_SUCCESS,
            "ma_sound_init_from_data_source"
        );
        ma_sound_set_start_time_in_pcm_frames(sound, start_frame);
        if let Some(stop_frame) = stop_frame {
            ma_sound_set_stop_time_in_pcm_frames(sound, stop_frame);
        }
        assert_eq!(ma_sound_start(sound), MA_SUCCESS, "ma_sound_start");

        let mut output = vec![0.0f32; total_frames];
        for period in output.chunks_mut(PERIOD) {
            let mut frames_read: ma_uint64 = 0;
            assert_eq!(
                ma_engine_read_pcm_frames(
                    engine,
                    period.as_mut_ptr() as *mut c_void,
                    period.len() as ma_uint64,
                    &mut frames_read,
                ),
                MA_SUCCESS,
                "ma_engine_read_pcm_frames"
            );
            assert_eq!(frames_read as usize, period.len(), "short graph read");
        }

        ma_sound_uninit(sound);
        ma_sound_free(sound);
        ma_audio_buffer_uninit(&mut buffer);
        ma_engine_uninit(engine);
        ma_engine_free(engine);
        output
    }
}

/// The frame at which a one-sample impulse scheduled at `start_frame`
/// arrives: the sound's start.
fn impulse_arrival_frame(start_frame: u64) -> usize {
    let mut impulse = vec![0.0f32; 64];
    impulse[0] = 1.0;
    let output = render(&impulse, start_frame, None, 4 * PERIOD);
    let (frame, peak) = output
        .iter()
        .enumerate()
        .fold((0usize, 0.0f32), |best, (index, sample)| {
            if sample.abs() > best.1 {
                (index, sample.abs())
            } else {
                best
            }
        });
    assert!(peak > 0.5, "no impulse in the rendered output (peak {peak})");
    frame
}

/// The frames that carry sound when a constant tone runs from
/// `start_frame` to `stop_frame`: the first and one past the last.
fn audible_span(start_frame: u64, stop_frame: u64) -> (usize, usize) {
    let tone = vec![1.0f32; 8 * PERIOD];
    let output = render(&tone, start_frame, Some(stop_frame), 4 * PERIOD);
    let first = output.iter().position(|sample| *sample != 0.0).expect("nothing audible");
    let last = output.iter().rposition(|sample| *sample != 0.0).expect("nothing audible");
    assert!(
        output[first..=last].iter().all(|sample| *sample == 1.0),
        "the tone was interrupted or altered between its first and last frame"
    );
    (first, last + 1)
}

#[test]
fn start_inside_the_first_period_lands_on_its_frame() {
    assert_eq!(impulse_arrival_frame(100), 100);
}

#[test]
fn start_inside_a_later_period_lands_on_its_frame() {
    assert_eq!(impulse_arrival_frame(700), 700);
}

#[test]
fn start_on_a_period_boundary_lands_on_its_frame() {
    assert_eq!(impulse_arrival_frame(PERIOD as u64), PERIOD);
}

#[test]
fn immediate_start_lands_on_frame_zero() {
    assert_eq!(impulse_arrival_frame(0), 0);
}

#[test]
fn stop_inside_a_period_ends_on_its_frame() {
    assert_eq!(audible_span(0, 700), (0, 700));
}

#[test]
fn start_and_stop_inside_one_period_play_exactly_that_span() {
    assert_eq!(audible_span(100, 300), (100, 300));
}

#[test]
fn start_and_stop_in_different_periods_play_exactly_that_span() {
    assert_eq!(audible_span(700, 1300), (700, 1300));
}
