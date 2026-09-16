require 'json'

package = JSON.parse(File.read(File.join(__dir__, '..', 'package.json')))
repository_root = File.expand_path('../../../..', __dir__)
steam_audio_dir = File.join(repository_root, 'cosmos', 'steamaudio-sys', 'phonon')
miniaudio_dir = File.join(repository_root, 'cosmos', 'miniaudio-sys', 'miniaudio')
cosmos_audio_dir = File.join(repository_root, 'cosmos', 'cosmos-audio', 'csrc')

Pod::Spec.new do |s|
  s.name = 'PlayAuralSpatialAudio'
  s.version = package['version']
  s.summary = 'Route-safe native Steam Audio HRTF rendering for PlayAural'
  s.license = package['license']
  s.author = 'PlayAural contributors'
  s.homepage = 'https://github.com/Daoductrung/PlayAural'
  s.platforms = { :ios => '15.1' }
  s.swift_version = '5.9'
  s.source = { git: 'https://github.com/Daoductrung/PlayAural.git' }
  s.static_framework = true

  s.dependency 'ExpoModulesCore'
  s.source_files = '*.{h,m,swift}'
  s.public_header_files = 'PlayAuralSpatialAudioBridge.h'
  s.frameworks = 'Accelerate', 'AudioToolbox', 'AVFoundation', 'CoreAudio'
  s.libraries = 'c++'

  s.pod_target_xcconfig = {
    'CLANG_C_LANGUAGE_STANDARD' => 'c11',
    'DEFINES_MODULE' => 'YES',
    'HEADER_SEARCH_PATHS' => "\"#{cosmos_audio_dir}\" \"#{miniaudio_dir}\" \"#{steam_audio_dir}\"",
    'LIBRARY_SEARCH_PATHS[sdk=iphoneos*]' => "\"#{File.join(steam_audio_dir, 'ios')}\"",
    'OTHER_LDFLAGS[sdk=iphoneos*]' => '$(inherited) -lphonon'
  }
end
