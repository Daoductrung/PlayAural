//! Window and keyboard input for Cosmos audio game library.
//!
//! Provides a simple window for receiving keyboard input in audio games.

use winit::application::ApplicationHandler;
use winit::event::{ElementState, KeyEvent, WindowEvent};
use winit::event_loop::{ActiveEventLoop, ControlFlow, EventLoop, EventLoopProxy};
use winit::keyboard::{KeyCode, PhysicalKey};
use winit::window::{Window as WinitWindow, WindowId};

/// Keyboard key codes.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[repr(i32)]
pub enum Key {
    // Letters
    A = 4,
    B = 5,
    C = 6,
    D = 7,
    E = 8,
    F = 9,
    G = 10,
    H = 11,
    I = 12,
    J = 13,
    K = 14,
    L = 15,
    M = 16,
    N = 17,
    O = 18,
    P = 19,
    Q = 20,
    R = 21,
    S = 22,
    T = 23,
    U = 24,
    V = 25,
    W = 26,
    X = 27,
    Y = 28,
    Z = 29,

    // Numbers
    N0 = 39,
    N1 = 30,
    N2 = 31,
    N3 = 32,
    N4 = 33,
    N5 = 34,
    N6 = 35,
    N7 = 36,
    N8 = 37,
    N9 = 38,

    // Function keys
    F1 = 58,
    F2 = 59,
    F3 = 60,
    F4 = 61,
    F5 = 62,
    F6 = 63,
    F7 = 64,
    F8 = 65,
    F9 = 66,
    F10 = 67,
    F11 = 68,
    F12 = 69,

    // Special keys
    Escape = 41,
    Enter = 40,
    Space = 44,
    Tab = 43,
    Backspace = 42,

    // Arrow keys
    Up = 82,
    Down = 81,
    Left = 80,
    Right = 79,

    // Modifiers
    LShift = 225,
    RShift = 229,
    LCtrl = 224,
    RCtrl = 228,
    LAlt = 226,
    RAlt = 230,

    // Navigation
    Insert = 73,
    Delete = 76,
    Home = 74,
    End = 77,
    PageUp = 75,
    PageDown = 78,

    // Punctuation
    Minus = 45,
    Equals = 46,
    LeftBracket = 47,
    RightBracket = 48,
    Backslash = 49,
    Semicolon = 51,
    Apostrophe = 52,
    Grave = 53,
    Comma = 54,
    Period = 55,
    Slash = 56,

    // Numpad
    Kp0 = 98,
    Kp1 = 89,
    Kp2 = 90,
    Kp3 = 91,
    Kp4 = 92,
    Kp5 = 93,
    Kp6 = 94,
    Kp7 = 95,
    Kp8 = 96,
    Kp9 = 97,
    KpEnter = 88,
    KpPlus = 87,
    KpMinus = 86,
    KpMultiply = 85,
    KpDivide = 84,
    KpPeriod = 99,
}

impl Key {
    /// Get the raw scancode value.
    pub fn as_i32(self) -> i32 {
        self as i32
    }
}

fn keycode_to_scancode(key: KeyCode) -> Option<i32> {
    Some(match key {
        KeyCode::KeyA => Key::A as i32,
        KeyCode::KeyB => Key::B as i32,
        KeyCode::KeyC => Key::C as i32,
        KeyCode::KeyD => Key::D as i32,
        KeyCode::KeyE => Key::E as i32,
        KeyCode::KeyF => Key::F as i32,
        KeyCode::KeyG => Key::G as i32,
        KeyCode::KeyH => Key::H as i32,
        KeyCode::KeyI => Key::I as i32,
        KeyCode::KeyJ => Key::J as i32,
        KeyCode::KeyK => Key::K as i32,
        KeyCode::KeyL => Key::L as i32,
        KeyCode::KeyM => Key::M as i32,
        KeyCode::KeyN => Key::N as i32,
        KeyCode::KeyO => Key::O as i32,
        KeyCode::KeyP => Key::P as i32,
        KeyCode::KeyQ => Key::Q as i32,
        KeyCode::KeyR => Key::R as i32,
        KeyCode::KeyS => Key::S as i32,
        KeyCode::KeyT => Key::T as i32,
        KeyCode::KeyU => Key::U as i32,
        KeyCode::KeyV => Key::V as i32,
        KeyCode::KeyW => Key::W as i32,
        KeyCode::KeyX => Key::X as i32,
        KeyCode::KeyY => Key::Y as i32,
        KeyCode::KeyZ => Key::Z as i32,
        KeyCode::Digit0 => Key::N0 as i32,
        KeyCode::Digit1 => Key::N1 as i32,
        KeyCode::Digit2 => Key::N2 as i32,
        KeyCode::Digit3 => Key::N3 as i32,
        KeyCode::Digit4 => Key::N4 as i32,
        KeyCode::Digit5 => Key::N5 as i32,
        KeyCode::Digit6 => Key::N6 as i32,
        KeyCode::Digit7 => Key::N7 as i32,
        KeyCode::Digit8 => Key::N8 as i32,
        KeyCode::Digit9 => Key::N9 as i32,
        KeyCode::F1 => Key::F1 as i32,
        KeyCode::F2 => Key::F2 as i32,
        KeyCode::F3 => Key::F3 as i32,
        KeyCode::F4 => Key::F4 as i32,
        KeyCode::F5 => Key::F5 as i32,
        KeyCode::F6 => Key::F6 as i32,
        KeyCode::F7 => Key::F7 as i32,
        KeyCode::F8 => Key::F8 as i32,
        KeyCode::F9 => Key::F9 as i32,
        KeyCode::F10 => Key::F10 as i32,
        KeyCode::F11 => Key::F11 as i32,
        KeyCode::F12 => Key::F12 as i32,
        KeyCode::Escape => Key::Escape as i32,
        KeyCode::Enter => Key::Enter as i32,
        KeyCode::Space => Key::Space as i32,
        KeyCode::Tab => Key::Tab as i32,
        KeyCode::Backspace => Key::Backspace as i32,
        KeyCode::ArrowUp => Key::Up as i32,
        KeyCode::ArrowDown => Key::Down as i32,
        KeyCode::ArrowLeft => Key::Left as i32,
        KeyCode::ArrowRight => Key::Right as i32,
        KeyCode::ShiftLeft => Key::LShift as i32,
        KeyCode::ShiftRight => Key::RShift as i32,
        KeyCode::ControlLeft => Key::LCtrl as i32,
        KeyCode::ControlRight => Key::RCtrl as i32,
        KeyCode::AltLeft => Key::LAlt as i32,
        KeyCode::AltRight => Key::RAlt as i32,
        KeyCode::Insert => Key::Insert as i32,
        KeyCode::Delete => Key::Delete as i32,
        KeyCode::Home => Key::Home as i32,
        KeyCode::End => Key::End as i32,
        KeyCode::PageUp => Key::PageUp as i32,
        KeyCode::PageDown => Key::PageDown as i32,
        KeyCode::Minus => Key::Minus as i32,
        KeyCode::Equal => Key::Equals as i32,
        KeyCode::BracketLeft => Key::LeftBracket as i32,
        KeyCode::BracketRight => Key::RightBracket as i32,
        KeyCode::Backslash => Key::Backslash as i32,
        KeyCode::Semicolon => Key::Semicolon as i32,
        KeyCode::Quote => Key::Apostrophe as i32,
        KeyCode::Backquote => Key::Grave as i32,
        KeyCode::Comma => Key::Comma as i32,
        KeyCode::Period => Key::Period as i32,
        KeyCode::Slash => Key::Slash as i32,
        KeyCode::Numpad0 => Key::Kp0 as i32,
        KeyCode::Numpad1 => Key::Kp1 as i32,
        KeyCode::Numpad2 => Key::Kp2 as i32,
        KeyCode::Numpad3 => Key::Kp3 as i32,
        KeyCode::Numpad4 => Key::Kp4 as i32,
        KeyCode::Numpad5 => Key::Kp5 as i32,
        KeyCode::Numpad6 => Key::Kp6 as i32,
        KeyCode::Numpad7 => Key::Kp7 as i32,
        KeyCode::Numpad8 => Key::Kp8 as i32,
        KeyCode::Numpad9 => Key::Kp9 as i32,
        KeyCode::NumpadEnter => Key::KpEnter as i32,
        KeyCode::NumpadAdd => Key::KpPlus as i32,
        KeyCode::NumpadSubtract => Key::KpMinus as i32,
        KeyCode::NumpadMultiply => Key::KpMultiply as i32,
        KeyCode::NumpadDivide => Key::KpDivide as i32,
        KeyCode::NumpadDecimal => Key::KpPeriod as i32,
        _ => return None,
    })
}

/// User event for controlling the event loop from outside.
#[derive(Debug, Clone)]
enum UserEvent {
    Close,
}

/// Window for receiving keyboard input.
pub struct Window {
    running: bool,
    keys_down: [bool; 512],
    keys_down_prev: [bool; 512],
    keys_repeat: [bool; 512],
    event_loop: Option<EventLoop<UserEvent>>,
    proxy: EventLoopProxy<UserEvent>,
    handler: WinitHandler,
}

struct WinitHandler {
    window: Option<WinitWindow>,
    title: String,
    close_requested: bool,
    pending_keys: Vec<(i32, bool, bool)>, // (scancode, pressed, repeat)
}

impl ApplicationHandler<UserEvent> for WinitHandler {
    fn resumed(&mut self, event_loop: &ActiveEventLoop) {
        if self.window.is_none() {
            let attrs = WinitWindow::default_attributes()
                .with_title(&self.title)
                .with_inner_size(winit::dpi::LogicalSize::new(1, 1));
            self.window = Some(event_loop.create_window(attrs).unwrap());
        }
    }

    fn user_event(&mut self, event_loop: &ActiveEventLoop, event: UserEvent) {
        match event {
            UserEvent::Close => {
                self.close_requested = true;
                event_loop.exit();
            }
        }
    }

    fn window_event(&mut self, event_loop: &ActiveEventLoop, _id: WindowId, event: WindowEvent) {
        match event {
            WindowEvent::CloseRequested => {
                self.close_requested = true;
                event_loop.exit();
            }
            WindowEvent::KeyboardInput {
                event:
                    KeyEvent {
                        physical_key: PhysicalKey::Code(key),
                        state,
                        repeat,
                        ..
                    },
                ..
            } => {
                if let Some(scancode) = keycode_to_scancode(key) {
                    let pressed = state == ElementState::Pressed;
                    self.pending_keys.push((scancode, pressed, repeat));
                }
            }
            _ => {}
        }
    }
}

impl Window {
    /// Create a new window with the given title.
    pub fn new(title: &str) -> Result<Self, String> {
        let event_loop = EventLoop::<UserEvent>::with_user_event()
            .build()
            .map_err(|e| format!("Failed to create event loop: {}", e))?;
        event_loop.set_control_flow(ControlFlow::Poll);

        let proxy = event_loop.create_proxy();

        let handler = WinitHandler {
            window: None,
            title: title.to_string(),
            close_requested: false,
            pending_keys: Vec::new(),
        };

        let mut window = Self {
            running: true,
            keys_down: [false; 512],
            keys_down_prev: [false; 512],
            keys_repeat: [false; 512],
            event_loop: Some(event_loop),
            proxy,
            handler,
        };

        // Do an initial pump to create the window
        window.update();

        Ok(window)
    }

    /// Destroy the window and release resources.
    pub fn destroy(&mut self) {
        self.running = false;
        self.handler.window = None;
        self.event_loop = None;
    }

    /// Check if the window is still open.
    pub fn is_open(&self) -> bool {
        self.running
    }

    /// Close the window.
    pub fn close(&mut self) {
        self.running = false;
        let _ = self.proxy.send_event(UserEvent::Close);
    }

    /// Update the window and process events. Call once per frame.
    pub fn update(&mut self) {
        // Copy current state to previous
        self.keys_down_prev = self.keys_down;

        // Clear per-frame state
        self.keys_repeat = [false; 512];

        // Pump events from the event loop (non-blocking)
        if let Some(event_loop) = self.event_loop.take() {
            use winit::platform::pump_events::EventLoopExtPumpEvents;
            let mut event_loop = event_loop;
            let status = event_loop.pump_app_events(Some(std::time::Duration::ZERO), &mut self.handler);

            // Check if event loop wants to exit
            if let winit::platform::pump_events::PumpStatus::Exit(_) = status {
                self.running = false;
            }

            self.event_loop = Some(event_loop);
        }

        // Check if close was requested
        if self.handler.close_requested {
            self.running = false;
        }

        // Process accumulated key events
        for &(scancode, pressed, repeat) in &self.handler.pending_keys {
            if (scancode as usize) < 512 {
                if pressed {
                    self.keys_down[scancode as usize] = true;
                    if repeat {
                        self.keys_repeat[scancode as usize] = true;
                    }
                } else {
                    self.keys_down[scancode as usize] = false;
                }
            }
        }
        self.handler.pending_keys.clear();
    }

    /// Check if a key was pressed this frame.
    pub fn key_pressed(&self, key: Key) -> bool {
        let code = key as usize;
        code < 512 && self.keys_down[code] && !self.keys_down_prev[code]
    }

    /// Check if a key is being held down.
    pub fn key_held(&self, key: Key) -> bool {
        let code = key as usize;
        code < 512 && self.keys_down[code]
    }

    /// Check if a key was released this frame.
    pub fn key_released(&self, key: Key) -> bool {
        let code = key as usize;
        code < 512 && !self.keys_down[code] && self.keys_down_prev[code]
    }

    /// Check if a key is repeating (OS key repeat).
    pub fn key_repeating(&self, key: Key) -> bool {
        let code = key as usize;
        code < 512 && self.keys_repeat[code]
    }

    /// Check if a key was pressed this frame or is repeating.
    pub fn key_pressed_or_repeating(&self, key: Key) -> bool {
        self.key_pressed(key) || self.key_repeating(key)
    }

    /// Check key state by raw scancode.
    pub fn key_pressed_raw(&self, code: i32) -> bool {
        let code = code as usize;
        code < 512 && self.keys_down[code] && !self.keys_down_prev[code]
    }

    /// Check key held state by raw scancode.
    pub fn key_held_raw(&self, code: i32) -> bool {
        let code = code as usize;
        code < 512 && self.keys_down[code]
    }

    /// Check key released state by raw scancode.
    pub fn key_released_raw(&self, code: i32) -> bool {
        let code = code as usize;
        code < 512 && !self.keys_down[code] && self.keys_down_prev[code]
    }
}
