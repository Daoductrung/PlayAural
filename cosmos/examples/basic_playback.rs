//! Basic audio playback example demonstrating 3D positioning and HRTF.
//!
//! Run with: cargo run --example basic_playback

use cosmos_audio::{SoundManager, Result};
use std::thread;
use std::time::Duration;

fn main() -> Result<()> {
    println!("Cosmos Audio - Basic Playback Example");
    println!("======================================");

    // Create the sound manager
    let mut manager = SoundManager::new()?;

    println!("Audio engine initialized");
    println!("Sample rate: {} Hz", manager.sample_rate());
    println!("HRTF available: {}", manager.is_hrtf_available());

    // Create a sound
    let mut sound = manager.create_sound();

    // Load an audio file (you'll need to provide your own audio file)
    // Uncomment and modify the path to test with an actual file:
    // sound.load("path/to/your/audio.ogg")?;

    // Example: Position the sound to the right of the listener
    sound.set_position(5.0, 0.0, 0.0);

    // Enable HRTF for immersive 3D audio
    sound.set_hrtf(true);

    // Set volume
    sound.set_volume(0.8);

    // Set looping
    sound.set_looping(true);

    // Play the sound
    // sound.play()?;

    println!("\nSound properties:");
    println!("  Position: ({}, {}, {})", sound.x(), sound.y(), sound.z());
    println!("  Volume: {}", sound.volume());
    println!("  HRTF enabled: {}", sound.hrtf());
    println!("  Looping: {}", sound.is_looping());

    // Simulate a game loop that updates the listener position
    println!("\nSimulating listener movement...");

    for i in 0..10 {
        // Move the listener in a circle
        let angle = (i as f32) * 36.0; // 36 degrees per step
        let x = angle.to_radians().cos() * 2.0;
        let y = angle.to_radians().sin() * 2.0;

        manager.set_listener(x, y, 0.0, angle);

        // In a real game, you would also call update_spatialization on each sound
        // that needs to track listener movement

        println!("  Listener at ({:.2}, {:.2}), facing {:.0} degrees",
                 manager.listener_x(),
                 manager.listener_y(),
                 manager.listener_angle());

        thread::sleep(Duration::from_millis(100));
    }

    println!("\nExample complete!");

    Ok(())
}
