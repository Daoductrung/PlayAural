use std::env;
use std::path::PathBuf;

// Stage the Steam Audio runtime and its distribution notices into OUT_DIR so
// maturin can include one complete, reviewable runtime set in the wheel. The
// built `cosmos.pyd` links against phonon and needs the DLL next to the
// extension; the notices live in a package data subdirectory.
fn main() {
    #[cfg(target_os = "windows")]
    {
        let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap());
        let out_dir = PathBuf::from(env::var("OUT_DIR").unwrap());

        let phonon_dir = manifest_dir
            .join("..")
            .join("steamaudio-sys")
            .join("phonon");
        let dll_src = phonon_dir.join("phonon.dll");
        let dll_dst = out_dir.join("phonon.dll");

        std::fs::copy(&dll_src, &dll_dst).unwrap_or_else(|e| {
            panic!(
                "Failed to copy {} -> {}: {e}",
                dll_src.display(),
                dll_dst.display()
            )
        });

        println!("cargo:rerun-if-changed={}", dll_src.display());

        let notice_out_dir = out_dir.join("steam_audio");
        std::fs::create_dir_all(&notice_out_dir).unwrap_or_else(|e| {
            panic!(
                "Failed to create Steam Audio notice directory {}: {e}",
                notice_out_dir.display()
            )
        });
        for name in [
            "LICENSE.md",
            "THIRDPARTY.md",
            "TRADEMARK_RIGHTS.md",
            "UPSTREAM.json",
        ] {
            let source = phonon_dir.join(name);
            let destination = notice_out_dir.join(name);
            std::fs::copy(&source, &destination).unwrap_or_else(|e| {
                panic!(
                    "Failed to copy {} -> {}: {e}",
                    source.display(),
                    destination.display()
                )
            });
            println!("cargo:rerun-if-changed={}", source.display());
        }
    }
}
