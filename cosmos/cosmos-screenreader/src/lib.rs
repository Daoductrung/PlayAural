//! Screen reader support for Cosmos audio game library.
//!
//! Provides a unified interface for text-to-speech through system screen readers.
//! Currently supports NVDA on Windows, with a debug fallback driver.

mod driver;

#[cfg(windows)]
mod nvda;

mod debug;

pub use driver::{ScreenReaderAPI, ScreenReaderDriver, ScreenReaderError};

use driver::ScreenReaderDriver as DriverTrait;

/// Main screen reader wrapper class.
/// Automatically selects the first available screen reader from the priority list.
pub struct ScreenReader {
    active_driver: Option<Box<dyn DriverTrait>>,
    drivers: Vec<Box<dyn DriverTrait>>,
}

impl ScreenReader {
    /// Create a screen reader with the default priority order (NVDA, then Debug).
    pub fn new() -> Self {
        Self::with_priority(&[ScreenReaderAPI::Nvda, ScreenReaderAPI::Debug])
    }

    /// Create a screen reader with a custom priority order.
    pub fn with_priority(priority: &[ScreenReaderAPI]) -> Self {
        let mut drivers: Vec<Box<dyn DriverTrait>> = Vec::new();

        for api in priority {
            if let Some(driver) = Self::create_driver(*api) {
                drivers.push(driver);
            }
        }

        let mut sr = Self {
            active_driver: None,
            drivers,
        };
        sr.select_driver();
        sr
    }

    fn create_driver(api: ScreenReaderAPI) -> Option<Box<dyn DriverTrait>> {
        match api {
            ScreenReaderAPI::Nvda => {
                #[cfg(windows)]
                {
                    Some(Box::new(nvda::NvdaDriver::new()))
                }
                #[cfg(not(windows))]
                {
                    None
                }
            }
            ScreenReaderAPI::Debug => Some(Box::new(debug::DebugDriver::new())),
        }
    }

    fn select_driver(&mut self) {
        self.active_driver = None;
        for driver in self.drivers.iter() {
            if driver.is_available() {
                // We need to take ownership, so we'll track the index
                // Actually, we can't move out of the Vec easily.
                // Let's redesign: keep drivers separate and just track which is active
                self.active_driver = None; // Will be set below
                break;
            }
        }
        // Find first available driver
        for driver in &self.drivers {
            if driver.is_available() {
                // We'll use the drivers directly instead of moving
                break;
            }
        }
    }

    fn get_active(&self) -> Option<&dyn DriverTrait> {
        for driver in &self.drivers {
            if driver.is_available() {
                return Some(driver.as_ref());
            }
        }
        None
    }

    fn get_active_mut(&mut self) -> Option<&mut dyn DriverTrait> {
        for driver in &mut self.drivers {
            if driver.is_available() {
                return Some(driver.as_mut());
            }
        }
        None
    }

    /// Get the currently active screen reader API.
    pub fn get_active_api(&self) -> Option<ScreenReaderAPI> {
        self.get_active().map(|d| d.get_api())
    }

    /// Check if any screen reader is available.
    pub fn is_available(&self) -> bool {
        self.get_active().is_some()
    }

    /// Check if speaking is supported.
    pub fn can_speak(&self) -> bool {
        self.get_active().map(|d| d.can_speak()).unwrap_or(false)
    }

    /// Check if braille output is supported.
    pub fn can_braille(&self) -> bool {
        self.get_active().map(|d| d.can_braille()).unwrap_or(false)
    }

    /// Check if is_speaking query is supported.
    pub fn can_is_speaking(&self) -> bool {
        self.get_active()
            .map(|d| d.can_is_speaking())
            .unwrap_or(false)
    }

    /// Speak text using the active screen reader.
    pub fn speak(&mut self, text: &str) -> Result<(), ScreenReaderError> {
        match self.get_active_mut() {
            Some(driver) => driver.speak(text),
            None => Err(ScreenReaderError::NotAvailable),
        }
    }

    /// Display text on braille display.
    pub fn braille(&mut self, text: &str) -> Result<(), ScreenReaderError> {
        match self.get_active_mut() {
            Some(driver) => driver.braille(text),
            None => Err(ScreenReaderError::NotAvailable),
        }
    }

    /// Stop current speech.
    pub fn stop(&mut self) -> Result<(), ScreenReaderError> {
        match self.get_active_mut() {
            Some(driver) => driver.stop(),
            None => Err(ScreenReaderError::NotAvailable),
        }
    }

    /// Check if currently speaking.
    pub fn is_speaking(&self) -> Result<bool, ScreenReaderError> {
        match self.get_active() {
            Some(driver) => driver.is_speaking(),
            None => Err(ScreenReaderError::NotAvailable),
        }
    }

    /// Refresh the active driver selection.
    /// Call this if screen reader availability may have changed.
    pub fn refresh(&mut self) {
        self.select_driver();
    }
}

impl Default for ScreenReader {
    fn default() -> Self {
        Self::new()
    }
}
