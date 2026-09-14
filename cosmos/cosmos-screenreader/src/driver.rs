//! Screen reader driver trait and common types.

use std::fmt;

/// Supported screen reader backends.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ScreenReaderAPI {
    /// NVDA screen reader (Windows only)
    Nvda,
    /// Debug driver that prints to console
    Debug,
}

/// Error type for screen reader operations.
#[derive(Debug)]
pub enum ScreenReaderError {
    /// No screen reader is available
    NotAvailable,
    /// The requested operation is not supported
    NotSupported,
    /// The operation failed
    OperationFailed(String),
}

impl fmt::Display for ScreenReaderError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ScreenReaderError::NotAvailable => write!(f, "No screen reader available"),
            ScreenReaderError::NotSupported => write!(f, "Operation not supported"),
            ScreenReaderError::OperationFailed(msg) => write!(f, "Operation failed: {}", msg),
        }
    }
}

impl std::error::Error for ScreenReaderError {}

/// Base trait for screen reader driver implementations.
pub trait ScreenReaderDriver: Send {
    /// Check if this driver is available and active.
    fn is_available(&self) -> bool;

    /// Get the API type of this driver.
    fn get_api(&self) -> ScreenReaderAPI;

    /// Check if speaking is supported.
    fn can_speak(&self) -> bool;

    /// Check if braille output is supported.
    fn can_braille(&self) -> bool;

    /// Check if is_speaking query is supported.
    fn can_is_speaking(&self) -> bool;

    /// Speak text.
    fn speak(&mut self, text: &str) -> Result<(), ScreenReaderError>;

    /// Display text on braille display.
    fn braille(&mut self, text: &str) -> Result<(), ScreenReaderError>;

    /// Stop current speech.
    fn stop(&mut self) -> Result<(), ScreenReaderError>;

    /// Check if currently speaking.
    fn is_speaking(&self) -> Result<bool, ScreenReaderError>;
}
