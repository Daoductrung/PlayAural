//! Debug screen reader driver that prints to console.

use crate::driver::{ScreenReaderAPI, ScreenReaderDriver, ScreenReaderError};

/// Debug driver that prints speech to the console.
/// Useful for testing when no screen reader is available.
pub struct DebugDriver {
    speaking: bool,
}

impl DebugDriver {
    /// Create a new debug driver.
    pub fn new() -> Self {
        Self { speaking: false }
    }
}

impl Default for DebugDriver {
    fn default() -> Self {
        Self::new()
    }
}

impl ScreenReaderDriver for DebugDriver {
    fn is_available(&self) -> bool {
        // Debug driver is always available as a fallback
        true
    }

    fn get_api(&self) -> ScreenReaderAPI {
        ScreenReaderAPI::Debug
    }

    fn can_speak(&self) -> bool {
        true
    }

    fn can_braille(&self) -> bool {
        true
    }

    fn can_is_speaking(&self) -> bool {
        true
    }

    fn speak(&mut self, text: &str) -> Result<(), ScreenReaderError> {
        println!("[ScreenReader] {}", text);
        self.speaking = false; // Instant "speech"
        Ok(())
    }

    fn braille(&mut self, text: &str) -> Result<(), ScreenReaderError> {
        println!("[Braille] {}", text);
        Ok(())
    }

    fn stop(&mut self) -> Result<(), ScreenReaderError> {
        self.speaking = false;
        Ok(())
    }

    fn is_speaking(&self) -> Result<bool, ScreenReaderError> {
        Ok(self.speaking)
    }
}
