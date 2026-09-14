//! Lock helper shared by the engine, sounds and groups.

use std::sync::{Mutex, MutexGuard};

/// Lock a mutex, recovering the guard if a previous holder panicked.
///
/// Audio state stays usable after a panic elsewhere (a poisoned lock holds
/// nothing that could be half-written in a harmful way: every field is a
/// plain value or a pointer miniaudio guards on its own side).
pub(crate) fn lock<T>(mutex: &Mutex<T>) -> MutexGuard<'_, T> {
    mutex.lock().unwrap_or_else(|poisoned| poisoned.into_inner())
}
