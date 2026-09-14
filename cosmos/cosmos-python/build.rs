use std::env;
use std::path::PathBuf;

// Stage phonon.dll (Steam Audio) into our OUT_DIR so maturin can pull it into the
// wheel right next to the compiled `cosmos` extension. The built `cosmos.pyd`
// links against phonon and needs the DLL findable at import time; CPython 3.8+
// loads extensions with LOAD_WITH_ALTERED_SEARCH_PATH, so a DLL sitting in the
// same directory as the .pyd resolves automatically. See pyproject.toml's
// [tool.maturin] include = [{ path = "phonon.dll", from = "out-dir", to = "" }].
fn main() {
    #[cfg(target_os = "windows")]
    {
        let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap());
        let out_dir = PathBuf::from(env::var("OUT_DIR").unwrap());

        let dll_src = manifest_dir
            .join("..")
            .join("steamaudio-sys")
            .join("phonon")
            .join("phonon.dll");
        let dll_dst = out_dir.join("phonon.dll");

        std::fs::copy(&dll_src, &dll_dst).unwrap_or_else(|e| {
            panic!(
                "Failed to copy {} -> {}: {e}",
                dll_src.display(),
                dll_dst.display()
            )
        });

        println!("cargo:rerun-if-changed={}", dll_src.display());
    }
}
