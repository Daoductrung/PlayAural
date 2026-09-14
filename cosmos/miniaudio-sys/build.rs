//! Compiles miniaudio. The Rust bindings in src/bindings.rs are committed;
//! they are regenerated only with the `regen-bindings` feature, which needs
//! libclang (`LIBCLANG_PATH`).

fn main() {
    cc::Build::new()
        .file("miniaudio/miniaudio_impl.c")
        .include("miniaudio")
        .define("MA_NO_WEBAUDIO", None)
        .define("MA_NO_NULL", None)
        .opt_level(2)
        .compile("miniaudio");

    println!("cargo:rerun-if-changed=miniaudio/miniaudio.h");
    println!("cargo:rerun-if-changed=miniaudio/miniaudio_impl.c");
    println!("cargo:rerun-if-changed=miniaudio/stb_vorbis.c");

    #[cfg(feature = "regen-bindings")]
    regenerate_bindings();
}

#[cfg(feature = "regen-bindings")]
fn regenerate_bindings() {
    use std::path::PathBuf;

    let manifest_dir = PathBuf::from(std::env::var("CARGO_MANIFEST_DIR").unwrap());

    let bindings = bindgen::Builder::default()
        .header("miniaudio/miniaudio.h")
        .clang_arg("-I./miniaudio")
        // Only generate bindings for what we need
        .allowlist_function("ma_engine_.*")
        .allowlist_function("ma_sound_.*")
        .allowlist_function("ma_node_.*")
        .allowlist_function("ma_decoder_.*")
        .allowlist_function("ma_resource_manager_.*")
        .allowlist_function("ma_audio_buffer.*")
        .allowlist_function("ma_data_source.*")
        .allowlist_function("ma_decoding_backend.*")
        .allowlist_function("ma_malloc")
        .allowlist_function("ma_free")
        .allowlist_function("ma_interleave_pcm_frames")
        .allowlist_function("ma_deinterleave_pcm_frames")
        .allowlist_function("ma_offset_pcm_frames_ptr_f32")
        .allowlist_function("ma_offset_pcm_frames_const_ptr_f32")
        .allowlist_type("ma_engine")
        .allowlist_type("ma_sound")
        .allowlist_type("ma_node.*")
        .allowlist_type("ma_decoder")
        .allowlist_type("ma_decoder_config")
        .allowlist_type("ma_audio_buffer.*")
        .allowlist_type("ma_data_source.*")
        .allowlist_type("ma_result")
        .allowlist_type("ma_bool32")
        .allowlist_type("ma_uint32")
        .allowlist_type("ma_uint64")
        .allowlist_type("ma_int32")
        .allowlist_type("ma_format")
        .allowlist_type("ma_resource_manager.*")
        .allowlist_type("ma_allocation_callbacks")
        .allowlist_var("ma_format_.*")
        // Don't double-prefix enum variants — we want `ma_format_f32`, not
        // `ma_format_ma_format_f32`. C names map straight through.
        .prepend_enum_name(false)
        // Layout tests can be slow and aren't strictly necessary
        .layout_tests(false)
        .generate()
        .expect("Failed to generate miniaudio bindings");

    bindings
        .write_to_file(manifest_dir.join("src").join("bindings.rs"))
        .expect("Failed to write miniaudio bindings");
}
