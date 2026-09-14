//! Links the bundled Steam Audio (Phonon) runtime. phonon.dll, phonon.lib and
//! the headers live in phonon/ next to this file. The Rust bindings in
//! src/bindings.rs are committed; they are regenerated only with the
//! `regen-bindings` feature, which needs libclang (`LIBCLANG_PATH`).

use std::env;
use std::path::PathBuf;

fn main() {
    let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap());
    let phonon_dir = manifest_dir.join("phonon");

    // Tell cargo to look for the phonon library in our bundled directory
    println!("cargo:rustc-link-search=native={}", phonon_dir.display());
    println!("cargo:rustc-link-lib=dylib=phonon");

    // Copy the DLL to the output directory for runtime
    #[cfg(target_os = "windows")]
    {
        let out_dir = PathBuf::from(env::var("OUT_DIR").unwrap());
        let dll_src = phonon_dir.join("phonon.dll");
        let dll_dst = out_dir.join("phonon.dll");
        if dll_src.exists() {
            std::fs::copy(&dll_src, &dll_dst).expect("Failed to copy phonon.dll");
        }
    }

    println!("cargo:rerun-if-changed=phonon/phonon.h");
    println!("cargo:rerun-if-changed=phonon/phonon_version.h");

    #[cfg(feature = "regen-bindings")]
    regenerate_bindings(&manifest_dir);
}

#[cfg(feature = "regen-bindings")]
fn regenerate_bindings(manifest_dir: &std::path::Path) {
    let bindings = bindgen::Builder::default()
        .header("phonon/phonon.h")
        .clang_arg("-I./phonon")
        // Include stdint.h for uint8_t and other standard integer types
        .clang_arg("-include")
        .clang_arg("stdint.h")
        // Allowlist Steam Audio types and functions
        .allowlist_function("ipl.*")
        .allowlist_type("IPL.*")
        .allowlist_var("IPL_.*")
        .allowlist_var("STEAMAUDIO_VERSION.*")
        // Layout tests can be slow
        .layout_tests(false)
        .generate()
        .expect("Failed to generate Steam Audio bindings");

    bindings
        .write_to_file(manifest_dir.join("src").join("bindings.rs"))
        .expect("Failed to write Steam Audio bindings");
}
