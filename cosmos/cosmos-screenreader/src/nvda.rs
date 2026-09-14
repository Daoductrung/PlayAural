//! NVDA screen reader driver using the NVDA Controller Client.

use crate::driver::{ScreenReaderAPI, ScreenReaderDriver, ScreenReaderError};
use std::ffi::OsStr;
use std::os::windows::ffi::OsStrExt;
use windows_sys::Win32::Foundation::HMODULE;
use windows_sys::Win32::System::LibraryLoader::{GetProcAddress, LoadLibraryW};

type TestIfRunningFunc = unsafe extern "C" fn() -> u32;
type SpeakTextFunc = unsafe extern "C" fn(*const u16) -> u32;
type CancelSpeechFunc = unsafe extern "C" fn() -> u32;
type BrailleMessageFunc = unsafe extern "C" fn(*const u16) -> u32;

/// NVDA screen reader driver.
pub struct NvdaDriver {
    nvda_lib: HMODULE,
    test_if_running: Option<TestIfRunningFunc>,
    speak_text: Option<SpeakTextFunc>,
    cancel_speech: Option<CancelSpeechFunc>,
    braille_message: Option<BrailleMessageFunc>,
}

// SAFETY: The NVDA functions are thread-safe according to NVDA documentation
unsafe impl Send for NvdaDriver {}

impl NvdaDriver {
    /// Create a new NVDA driver.
    pub fn new() -> Self {
        let mut driver = Self {
            nvda_lib: 0,
            test_if_running: None,
            speak_text: None,
            cancel_speech: None,
            braille_message: None,
        };
        driver.load_nvda();
        driver
    }

    fn load_nvda(&mut self) {
        // Try to load NVDA controller client DLL
        // First try 64-bit DLL name, then fall back to generic name
        let dll_names = [
            "nvdaControllerClient64.dll",
            "nvdaControllerClient.dll",
        ];

        for dll_name_str in &dll_names {
            let dll_name: Vec<u16> = OsStr::new(dll_name_str)
                .encode_wide()
                .chain(std::iter::once(0))
                .collect();

            let lib = unsafe { LoadLibraryW(dll_name.as_ptr()) };

            if lib != 0 {
                self.nvda_lib = lib;

                // Load function pointers
                self.test_if_running = Self::get_proc(lib, b"nvdaController_testIfRunning\0");
                self.speak_text = Self::get_proc(lib, b"nvdaController_speakText\0");
                self.cancel_speech = Self::get_proc(lib, b"nvdaController_cancelSpeech\0");
                self.braille_message = Self::get_proc(lib, b"nvdaController_brailleMessage\0");
                break;
            }
        }
    }

    fn get_proc<T>(lib: HMODULE, name: &[u8]) -> Option<T> {
        let proc = unsafe { GetProcAddress(lib, name.as_ptr()) };
        if proc.is_some() {
            Some(unsafe { std::mem::transmute_copy(&proc) })
        } else {
            None
        }
    }

    fn is_nvda_running(&self) -> bool {
        if let Some(test_func) = self.test_if_running {
            unsafe { test_func() == 0 }
        } else {
            false
        }
    }

    fn to_wide_string(s: &str) -> Vec<u16> {
        OsStr::new(s)
            .encode_wide()
            .chain(std::iter::once(0))
            .collect()
    }
}

// Note: We don't unload the DLL on drop since it stays loaded for the process lifetime.
// This is intentional as the NVDA controller client is typically used throughout the app.

impl Default for NvdaDriver {
    fn default() -> Self {
        Self::new()
    }
}

impl ScreenReaderDriver for NvdaDriver {
    fn is_available(&self) -> bool {
        self.is_nvda_running()
    }

    fn get_api(&self) -> ScreenReaderAPI {
        ScreenReaderAPI::Nvda
    }

    fn can_speak(&self) -> bool {
        self.is_nvda_running() && self.speak_text.is_some()
    }

    fn can_braille(&self) -> bool {
        self.is_nvda_running() && self.braille_message.is_some()
    }

    fn can_is_speaking(&self) -> bool {
        // NVDA controller client does not support this
        false
    }

    fn speak(&mut self, text: &str) -> Result<(), ScreenReaderError> {
        if !self.can_speak() {
            return Err(ScreenReaderError::NotAvailable);
        }

        let speak_func = self.speak_text.unwrap();
        let wide_text = Self::to_wide_string(text);
        let result = unsafe { speak_func(wide_text.as_ptr()) };

        if result == 0 {
            Ok(())
        } else {
            Err(ScreenReaderError::OperationFailed(
                "Failed to speak text".to_string(),
            ))
        }
    }

    fn braille(&mut self, text: &str) -> Result<(), ScreenReaderError> {
        if !self.can_braille() {
            return Err(ScreenReaderError::NotAvailable);
        }

        let braille_func = self.braille_message.unwrap();
        let wide_text = Self::to_wide_string(text);
        let result = unsafe { braille_func(wide_text.as_ptr()) };

        if result == 0 {
            Ok(())
        } else {
            Err(ScreenReaderError::OperationFailed(
                "Failed to display braille message".to_string(),
            ))
        }
    }

    fn stop(&mut self) -> Result<(), ScreenReaderError> {
        if !self.is_nvda_running() {
            return Err(ScreenReaderError::NotAvailable);
        }

        if let Some(cancel_func) = self.cancel_speech {
            let result = unsafe { cancel_func() };
            if result == 0 {
                Ok(())
            } else {
                Err(ScreenReaderError::OperationFailed(
                    "Failed to cancel speech".to_string(),
                ))
            }
        } else {
            Err(ScreenReaderError::NotSupported)
        }
    }

    fn is_speaking(&self) -> Result<bool, ScreenReaderError> {
        // NVDA controller client does not support this
        Err(ScreenReaderError::NotSupported)
    }
}
