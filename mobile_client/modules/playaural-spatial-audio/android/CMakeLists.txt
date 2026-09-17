cmake_minimum_required(VERSION 3.22.1)

project(playaural_spatial_audio LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(NOT DEFINED PLAYAURAL_REPOSITORY_ROOT)
  message(FATAL_ERROR "PLAYAURAL_REPOSITORY_ROOT is required")
endif()

set(COSMOS_AUDIO_DIR "${PLAYAURAL_REPOSITORY_ROOT}/cosmos/cosmos-audio/csrc")
set(MINIAUDIO_DIR "${PLAYAURAL_REPOSITORY_ROOT}/cosmos/miniaudio-sys/miniaudio")
set(STEAMAUDIO_DIR "${PLAYAURAL_REPOSITORY_ROOT}/cosmos/steamaudio-sys/phonon")

add_library(phonon SHARED IMPORTED)
set_target_properties(phonon PROPERTIES
  IMPORTED_LOCATION "${STEAMAUDIO_DIR}/android/${ANDROID_ABI}/libphonon.so"
)

add_library(
  playaural_spatial_audio
  SHARED
  src/main/c/NativeSpatialAudioBridge.c
  "${MINIAUDIO_DIR}/miniaudio_impl.c"
  "${COSMOS_AUDIO_DIR}/miniaudio_phonon.c"
  "${COSMOS_AUDIO_DIR}/cosmos_mobile.c"
)

target_compile_definitions(
  playaural_spatial_audio
  PRIVATE
  MA_NO_WEBAUDIO
  MA_NO_NULL
)
target_compile_options(
  playaural_spatial_audio
  PRIVATE
  -O2
  -Wall
  -Wextra
  -Werror=return-type
  -fstack-protector-strong
)
target_link_options(
  playaural_spatial_audio
  PRIVATE
  "-Wl,-z,max-page-size=16384"
)
target_include_directories(
  playaural_spatial_audio
  PRIVATE
  "${COSMOS_AUDIO_DIR}"
  "${MINIAUDIO_DIR}"
  "${STEAMAUDIO_DIR}"
)

find_library(ANDROID_LIBRARY android)
find_library(DL_LIBRARY dl)
find_library(LOG_LIBRARY log)
find_library(MATH_LIBRARY m)
find_library(OPENSL_LIBRARY OpenSLES)

target_link_libraries(
  playaural_spatial_audio
  phonon
  ${ANDROID_LIBRARY}
  ${DL_LIBRARY}
  ${LOG_LIBRARY}
  ${MATH_LIBRARY}
  ${OPENSL_LIBRARY}
  atomic
)
