#include <jni.h>
#include <stdint.h>
#include <stdlib.h>

#include "cosmos_mobile.h"

static jlongArray pointer_result(JNIEnv* env, void* pointer, cosmos_mobile_result result) {
    jlong values[2];
    jlongArray output = (*env)->NewLongArray(env, 2);
    if (output == NULL) {
        return NULL;
    }
    values[0] = (jlong)(intptr_t)pointer;
    values[1] = (jlong)result;
    (*env)->SetLongArrayRegion(env, output, 0, 2, values);
    return (*env)->ExceptionCheck(env) ? NULL : output;
}

JNIEXPORT jlongArray JNICALL
Java_one_ddt_playaural_spatialaudio_NativeSpatialAudioBridge_nativeCreateEngine(
    JNIEnv* env,
    jobject instance,
    jint hrtf_frame_size,
    jint parameter_smoothing_milliseconds,
    jint max_sources
) {
    cosmos_mobile_engine_config config;
    cosmos_mobile_result result;
    cosmos_mobile_engine* engine;
    (void)instance;
    config.hrtf_frame_size = (uint32_t)hrtf_frame_size;
    config.parameter_smoothing_milliseconds = (uint32_t)parameter_smoothing_milliseconds;
    config.max_sources = (uint32_t)max_sources;
    engine = cosmos_mobile_engine_create(&config, &result);
    jlongArray output = pointer_result(env, engine, result);
    if (output == NULL) {
        cosmos_mobile_engine_destroy(engine);
    }
    return output;
}

JNIEXPORT void JNICALL
Java_one_ddt_playaural_spatialaudio_NativeSpatialAudioBridge_nativeDestroyEngine(
    JNIEnv* env,
    jobject instance,
    jlong engine_handle
) {
    (void)env;
    (void)instance;
    cosmos_mobile_engine_destroy((cosmos_mobile_engine*)(intptr_t)engine_handle);
}

JNIEXPORT jint JNICALL
Java_one_ddt_playaural_spatialaudio_NativeSpatialAudioBridge_nativeEngineSampleRate(
    JNIEnv* env,
    jobject instance,
    jlong engine_handle
) {
    (void)env;
    (void)instance;
    return (jint)cosmos_mobile_engine_sample_rate(
        (cosmos_mobile_engine*)(intptr_t)engine_handle
    );
}

JNIEXPORT jlongArray JNICALL
Java_one_ddt_playaural_spatialaudio_NativeSpatialAudioBridge_nativeCreateSource(
    JNIEnv* env,
    jobject instance,
    jlong engine_handle,
    jstring intro_path,
    jstring loop_path,
    jstring outro_path,
    jboolean play_intro,
    jboolean looping,
    jboolean stream_from_disk,
    jboolean start_paused,
    jfloat volume,
    jfloat pitch,
    jfloat x,
    jfloat y,
    jfloat z,
    jfloat spatial_blend
) {
    const char* intro_chars = NULL;
    const char* loop_chars = NULL;
    const char* outro_chars = NULL;
    cosmos_mobile_source_config config = {0};
    cosmos_mobile_result result = COSMOS_MOBILE_INVALID_ARGUMENT;
    cosmos_mobile_source* source = NULL;
    (void)instance;

    if (loop_path == NULL) {
        return pointer_result(env, NULL, result);
    }
    loop_chars = (*env)->GetStringUTFChars(env, loop_path, NULL);
    if (loop_chars == NULL) {
        goto cleanup;
    }
    if (intro_path != NULL) {
        intro_chars = (*env)->GetStringUTFChars(env, intro_path, NULL);
        if (intro_chars == NULL) {
            goto cleanup;
        }
    }
    if (outro_path != NULL) {
        outro_chars = (*env)->GetStringUTFChars(env, outro_path, NULL);
        if (outro_chars == NULL) {
            goto cleanup;
        }
    }
    if (!(*env)->ExceptionCheck(env)) {
        config.intro_path = intro_chars;
        config.loop_path = loop_chars;
        config.outro_path = outro_chars;
        config.play_intro = play_intro ? 1 : 0;
        config.looping = looping ? 1 : 0;
        config.stream_from_disk = stream_from_disk ? 1 : 0;
        config.start_paused = start_paused ? 1 : 0;
        config.volume = volume;
        config.pitch = pitch;
        config.x = x;
        config.y = y;
        config.z = z;
        config.spatial_blend = spatial_blend;
        config.sequence_paths = NULL;
        config.sequence_count = 0;
        source = cosmos_mobile_source_create(
            (cosmos_mobile_engine*)(intptr_t)engine_handle,
            &config,
            &result
        );
    }
cleanup:
    if (outro_chars != NULL) {
        (*env)->ReleaseStringUTFChars(env, outro_path, outro_chars);
    }
    if (intro_chars != NULL) {
        (*env)->ReleaseStringUTFChars(env, intro_path, intro_chars);
    }
    if (loop_chars != NULL) {
        (*env)->ReleaseStringUTFChars(env, loop_path, loop_chars);
    }
    if ((*env)->ExceptionCheck(env)) {
        cosmos_mobile_source_destroy(source);
        return NULL;
    }
    jlongArray output = pointer_result(env, source, result);
    if (output == NULL) {
        cosmos_mobile_source_destroy(source);
    }
    return output;
}

JNIEXPORT jlongArray JNICALL
Java_one_ddt_playaural_spatialaudio_NativeSpatialAudioBridge_nativeCreateSequenceSource(
    JNIEnv* env,
    jobject instance,
    jlong engine_handle,
    jobjectArray sequence_paths,
    jboolean start_paused,
    jfloat volume,
    jfloat pitch,
    jfloat x,
    jfloat y,
    jfloat z,
    jfloat spatial_blend
) {
    jsize count;
    jsize index;
    jstring* path_strings = NULL;
    const char** path_chars = NULL;
    cosmos_mobile_source_config config = {0};
    cosmos_mobile_result result = COSMOS_MOBILE_INVALID_ARGUMENT;
    cosmos_mobile_source* source = NULL;
    (void)instance;

    if (sequence_paths == NULL) {
        return pointer_result(env, NULL, result);
    }
    count = (*env)->GetArrayLength(env, sequence_paths);
    if ((*env)->ExceptionCheck(env) || count <= 0 || count > 32) {
        return (*env)->ExceptionCheck(env) ? NULL : pointer_result(env, NULL, result);
    }
    path_strings = (jstring*)calloc((size_t)count, sizeof(*path_strings));
    path_chars = (const char**)calloc((size_t)count, sizeof(*path_chars));
    if (path_strings == NULL || path_chars == NULL) {
        result = COSMOS_MOBILE_OUT_OF_MEMORY;
        goto cleanup;
    }
    for (index = 0; index < count; index += 1) {
        path_strings[index] = (jstring)(*env)->GetObjectArrayElement(
            env,
            sequence_paths,
            index
        );
        if (path_strings[index] == NULL || (*env)->ExceptionCheck(env)) {
            goto cleanup;
        }
        path_chars[index] = (*env)->GetStringUTFChars(
            env,
            path_strings[index],
            NULL
        );
        if (path_chars[index] == NULL) {
            goto cleanup;
        }
    }
    config.loop_path = NULL;
    config.start_paused = start_paused ? 1 : 0;
    config.stream_from_disk = 0;
    config.volume = volume;
    config.pitch = pitch;
    config.x = x;
    config.y = y;
    config.z = z;
    config.spatial_blend = spatial_blend;
    config.sequence_paths = path_chars;
    config.sequence_count = (uint32_t)count;
    source = cosmos_mobile_source_create(
        (cosmos_mobile_engine*)(intptr_t)engine_handle,
        &config,
        &result
    );

cleanup:
    if (path_strings != NULL && path_chars != NULL) {
        for (index = 0; index < count; index += 1) {
            if (path_chars[index] != NULL) {
                (*env)->ReleaseStringUTFChars(
                    env,
                    path_strings[index],
                    path_chars[index]
                );
            }
            if (path_strings[index] != NULL) {
                (*env)->DeleteLocalRef(env, path_strings[index]);
            }
        }
    }
    free(path_chars);
    free(path_strings);
    if ((*env)->ExceptionCheck(env)) {
        cosmos_mobile_source_destroy(source);
        return NULL;
    }
    jlongArray output = pointer_result(env, source, result);
    if (output == NULL) {
        cosmos_mobile_source_destroy(source);
    }
    return output;
}

JNIEXPORT jlongArray JNICALL
Java_one_ddt_playaural_spatialaudio_NativeSpatialAudioBridge_nativeSequenceDurations(
    JNIEnv* env,
    jobject instance,
    jlong source_handle
) {
    jlong values[32];
    uint32_t count;
    uint32_t index;
    cosmos_mobile_source* source = (cosmos_mobile_source*)(intptr_t)source_handle;
    (void)instance;
    count = cosmos_mobile_source_sequence_count(source);
    if (count == 0 || count > 32) {
        return NULL;
    }
    for (index = 0; index < count; index += 1) {
        uint64_t duration = cosmos_mobile_source_sequence_duration_frames(source, index);
        values[index] = duration <= INT64_MAX ? (jlong)duration : 0;
    }
    jlongArray output = (*env)->NewLongArray(env, (jsize)count);
    if (output == NULL) {
        return NULL;
    }
    (*env)->SetLongArrayRegion(env, output, 0, (jsize)count, values);
    return (*env)->ExceptionCheck(env) ? NULL : output;
}

JNIEXPORT void JNICALL
Java_one_ddt_playaural_spatialaudio_NativeSpatialAudioBridge_nativeDestroySource(
    JNIEnv* env,
    jobject instance,
    jlong source_handle
) {
    (void)env;
    (void)instance;
    cosmos_mobile_source_destroy((cosmos_mobile_source*)(intptr_t)source_handle);
}

JNIEXPORT jint JNICALL
Java_one_ddt_playaural_spatialaudio_NativeSpatialAudioBridge_nativeSetParameters(
    JNIEnv* env,
    jobject instance,
    jlong source_handle,
    jfloat volume,
    jfloat pitch,
    jfloat x,
    jfloat y,
    jfloat z,
    jfloat spatial_blend
) {
    (void)env;
    (void)instance;
    return (jint)cosmos_mobile_source_set_parameters(
        (cosmos_mobile_source*)(intptr_t)source_handle,
        volume,
        pitch,
        x,
        y,
        z,
        spatial_blend
    );
}

JNIEXPORT jint JNICALL
Java_one_ddt_playaural_spatialaudio_NativeSpatialAudioBridge_nativePauseSource(
    JNIEnv* env,
    jobject instance,
    jlong source_handle
) {
    (void)env;
    (void)instance;
    return (jint)cosmos_mobile_source_pause(
        (cosmos_mobile_source*)(intptr_t)source_handle
    );
}

JNIEXPORT jint JNICALL
Java_one_ddt_playaural_spatialaudio_NativeSpatialAudioBridge_nativeResumeSource(
    JNIEnv* env,
    jobject instance,
    jlong source_handle
) {
    (void)env;
    (void)instance;
    return (jint)cosmos_mobile_source_resume(
        (cosmos_mobile_source*)(intptr_t)source_handle
    );
}

JNIEXPORT jint JNICALL
Java_one_ddt_playaural_spatialaudio_NativeSpatialAudioBridge_nativeRequestOutro(
    JNIEnv* env,
    jobject instance,
    jlong source_handle,
    jboolean finish_loop_boundary
) {
    (void)env;
    (void)instance;
    return (jint)cosmos_mobile_source_request_outro(
        (cosmos_mobile_source*)(intptr_t)source_handle,
        finish_loop_boundary ? 1 : 0
    );
}

JNIEXPORT void JNICALL
Java_one_ddt_playaural_spatialaudio_NativeSpatialAudioBridge_nativeStopSource(
    JNIEnv* env,
    jobject instance,
    jlong source_handle
) {
    (void)env;
    (void)instance;
    cosmos_mobile_source_stop((cosmos_mobile_source*)(intptr_t)source_handle);
}

JNIEXPORT jboolean JNICALL
Java_one_ddt_playaural_spatialaudio_NativeSpatialAudioBridge_nativeSourceAtEnd(
    JNIEnv* env,
    jobject instance,
    jlong source_handle
) {
    (void)env;
    (void)instance;
    return cosmos_mobile_source_at_end(
        (cosmos_mobile_source*)(intptr_t)source_handle
    ) ? JNI_TRUE : JNI_FALSE;
}
