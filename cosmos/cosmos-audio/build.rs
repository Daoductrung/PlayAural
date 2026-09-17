use std::env;
use std::path::PathBuf;

fn main() {
    let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap());
    let csrc_dir = manifest_dir.join("csrc");
    let miniaudio_dir = manifest_dir.join("../miniaudio-sys/miniaudio");
    let steamaudio_dir = manifest_dir.join("../steamaudio-sys/phonon");

    // Compile the miniaudio_phonon integration + the effect nodes (reverb,
    // EQ, disperser). Bundled into a single `miniaudio_phonon` static lib
    // for linker simplicity.
    cc::Build::new()
        .file(csrc_dir.join("miniaudio_phonon.c"))
        .file(csrc_dir.join("ma_convreverb.c"))
        .file(csrc_dir.join("ma_eq.c"))
        .file(csrc_dir.join("ma_disperser.c"))
        .file(csrc_dir.join("ma_filter.c"))
        .file(csrc_dir.join("ma_delay.c"))
        .file(csrc_dir.join("ma_distortion.c"))
        .file(csrc_dir.join("ma_vocoder.c"))
        .include(&csrc_dir)
        .include(&miniaudio_dir)
        .include(&steamaudio_dir)
        .std("c11")
        .flag_if_supported("/experimental:c11atomics")
        .opt_level(2)
        .compile("miniaudio_phonon");

    println!("cargo:rerun-if-changed=csrc/miniaudio_phonon.c");
    println!("cargo:rerun-if-changed=csrc/miniaudio_phonon.h");
    println!("cargo:rerun-if-changed=csrc/ma_convreverb.c");
    println!("cargo:rerun-if-changed=csrc/ma_convreverb.h");
    println!("cargo:rerun-if-changed=csrc/ma_eq.c");
    println!("cargo:rerun-if-changed=csrc/ma_eq.h");
    println!("cargo:rerun-if-changed=csrc/ma_disperser.c");
    println!("cargo:rerun-if-changed=csrc/ma_disperser.h");
    println!("cargo:rerun-if-changed=csrc/ma_filter.c");
    println!("cargo:rerun-if-changed=csrc/ma_filter.h");
    println!("cargo:rerun-if-changed=csrc/ma_delay.c");
    println!("cargo:rerun-if-changed=csrc/ma_delay.h");
    println!("cargo:rerun-if-changed=csrc/ma_distortion.c");
    println!("cargo:rerun-if-changed=csrc/ma_distortion.h");
    println!("cargo:rerun-if-changed=csrc/ma_vocoder.c");
    println!("cargo:rerun-if-changed=csrc/ma_vocoder.h");
    println!("cargo:rerun-if-changed=../miniaudio-sys/miniaudio/miniaudio.h");
    println!("cargo:rerun-if-changed=../steamaudio-sys/phonon/phonon.h");
    println!("cargo:rerun-if-changed=../steamaudio-sys/phonon/phonon_version.h");
}
