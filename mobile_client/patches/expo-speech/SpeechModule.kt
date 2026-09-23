// PlayAural lifecycle repair for expo-speech. Based on Expo's MIT-licensed
// SpeechModule; installed only against the reviewed upstream source hash.
package expo.modules.speech

import android.content.pm.ApplicationInfo
import android.media.AudioAttributes
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.speech.tts.Voice
import android.util.Log
import expo.modules.kotlin.Promise
import expo.modules.kotlin.functions.Queues
import expo.modules.kotlin.modules.Module
import expo.modules.kotlin.modules.ModuleDefinition
import expo.modules.kotlin.records.Field
import expo.modules.kotlin.records.Record
import java.util.Locale

private const val TAG = "PlayAuralTTS"
private const val STARTED = "Exponent.speakingStarted"
private const val BOUNDARY = "Exponent.speakingWillSayNextString"
private const val DONE = "Exponent.speakingDone"
private const val STOPPED = "Exponent.speakingStopped"
private const val ERROR = "Exponent.speakingError"

class SpeechModule : Module() {
  // All engine state and callbacks are serialized on the main looper. In
  // particular onInit can run before the constructor returns on some engines.
  private val handler = Handler(Looper.getMainLooper())
  private var engine: TextToSpeech? = null
  private var ready = false
  private var generation = 0L
  private var selectedEngine: String? = null
  private var engineCatalogReady = false
  private var availableEngines = emptyList<EngineRecord>()
  private val pendingSpeech = linkedMapOf<String, Utterance>()
  private val activeIds = mutableSetOf<String>()
  private val pendingEngines = mutableListOf<Promise>()
  private val pendingVoices = mutableListOf<Promise>()

  override fun definition() = ModuleDefinition {
    Name("ExpoSpeech")
    Events(STARTED, BOUNDARY, DONE, STOPPED, ERROR)
    Constant("maxSpeechInputLength") { TextToSpeech.getMaxSpeechInputLength() }

    // An Activity can be recreated while this module survives. Never retain a
    // permanently shut-down lazy singleton, or create one just to destroy it.
    OnActivityDestroys { handler.post { retire("Activity destroyed") } }
    OnDestroy { handler.post { retire("Module destroyed") } }

    AsyncFunction("reset") {
      selectedEngine = null
      engineCatalogReady = false
      availableEngines = emptyList()
      retire("Speech context changed")
    }.runOnQueue(Queues.MAIN)
    AsyncFunction("setEngine") { identifier: String ->
      val normalized = identifier.trim()
      require(normalized.isNotEmpty() && availableEngines.any { it.identifier == normalized }) {
        "Speech engine is not installed"
      }
      selectedEngine = normalized
      retire("Speech engine changed")
    }.runOnQueue(Queues.MAIN)
    AsyncFunction("stop") { stopSpeech() }.runOnQueue(Queues.MAIN)
    AsyncFunction<Boolean>("isSpeaking") { ready && engine?.isSpeaking == true }.runOnQueue(Queues.MAIN)
    AsyncFunction("getEngines") { promise: Promise ->
      if (engineCatalogReady) promise.resolve(availableEngines) else {
        pendingEngines.add(promise)
        ensureEngine()
      }
    }.runOnQueue(Queues.MAIN)
    AsyncFunction("getVoices") { promise: Promise ->
      if (ready) resolveVoices(promise) else {
        pendingVoices.add(promise)
        ensureEngine()
      }
    }.runOnQueue(Queues.MAIN)
    AsyncFunction("speak") { id: String, text: String, options: SpeechOptions ->
      if (text.length > TextToSpeech.getMaxSpeechInputLength()) throw SpeechInputIsToLongException()
      val utterance = Utterance(id, text, options)
      activeIds.add(id)
      if (ready) speakOut(utterance) else {
        pendingSpeech[id] = utterance
        ensureEngine()
      }
      Unit
    }.runOnQueue(Queues.MAIN)
  }

  private fun ensureEngine() {
    if (engine != null) return
    val current = ++generation
    Log.d(TAG, "Binding speech engine; generation=$current; selected=${selectedEngine ?: "system"}")
    try {
      val context = appContext.reactContext?.applicationContext
        ?: throw IllegalStateException("Speech application context is unavailable")
      engine = if (selectedEngine == null) TextToSpeech(context) { status ->
        finishEngineInitialization(current, status)
      } else TextToSpeech(context, { status ->
        finishEngineInitialization(current, status)
      }, selectedEngine)
    } catch (error: Exception) {
      failEngine(error.message ?: "Speech engine binding failed")
    }
  }

  private fun finishEngineInitialization(current: Long, status: Int) {
    handler.post {
      if (current != generation) return@post
      val tts = engine ?: return@post
      cacheAndResolveEngines(tts)
      if (status != TextToSpeech.SUCCESS) {
        failEngine("Speech engine initialization failed: $status")
        return@post
      }
      try {
        tts.setAudioAttributes(AudioAttributes.Builder()
          .setUsage(AudioAttributes.USAGE_MEDIA)
          .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
          .build())
        tts.setOnUtteranceProgressListener(listener(current))
        ready = true
        Log.d(TAG, "Speech engine ready; generation=$current")
        val requests = pendingVoices.toList()
        pendingVoices.clear()
        requests.forEach(::resolveVoices)
        val utterances = pendingSpeech.values.toList()
        pendingSpeech.clear()
        utterances.forEach(::speakOut)
      } catch (error: Exception) {
        failEngine(error.message ?: "Speech engine setup failed")
      }
    }
  }

  private fun cacheAndResolveEngines(tts: TextToSpeech) {
    try {
      val defaultEngine = tts.defaultEngine
      val packageManager = appContext.reactContext?.applicationContext?.packageManager
      availableEngines = tts.engines.map { info ->
        val isSystem = try {
          val flags = packageManager?.getApplicationInfo(info.name, 0)?.flags ?: 0
          flags and (ApplicationInfo.FLAG_SYSTEM or ApplicationInfo.FLAG_UPDATED_SYSTEM_APP) != 0
        } catch (_: Exception) {
          false
        }
        EngineRecord(
          identifier = info.name,
          label = info.label ?: info.name,
          isDefault = info.name == defaultEngine,
          isSystem = isSystem
        )
      }.distinctBy { it.identifier }
      engineCatalogReady = true
      val requests = pendingEngines.toList()
      pendingEngines.clear()
      requests.forEach { it.resolve(availableEngines) }
    } catch (error: Exception) {
      val requests = pendingEngines.toList()
      pendingEngines.clear()
      requests.forEach { it.reject("ERR_SPEECH_ENGINES", error.message ?: "Unable to list speech engines", error) }
    }
  }

  private fun resolveVoices(promise: Promise) {
    try {
      val voices = engine?.voices ?: throw SpeechUnableToGetVoicesException()
      promise.resolve(voices.map {
        VoiceRecord(
          identifier = it.name,
          name = it.name,
          quality = if (it.quality > Voice.QUALITY_NORMAL) VoiceQuality.ENHANCED else VoiceQuality.DEFAULT,
          language = LanguageUtils.getISOCode(it.locale)
        )
      })
    } catch (error: Exception) {
      promise.reject(SpeechUnableToGetVoicesException(error))
    }
  }

  private fun speakOut(utterance: Utterance) {
    val tts = engine ?: return
    val (id, text, options) = utterance
    if (id !in activeIds) return
    try {
      options.pitch?.let(tts::setPitch)
      options.rate?.let(tts::setSpeechRate)
      val voices = tts.voices.orEmpty()
      val requestedVoice = options.voice?.let { name -> voices.firstOrNull { it.name == name } }
      if (requestedVoice != null && tts.setVoice(requestedVoice) == TextToSpeech.SUCCESS) {
        // The explicit voice determines its locale.
      } else {
        val locale = options.language?.let { Locale.forLanguageTag(it.replace('_', '-')) }
        val supported = locale != null && tts.isLanguageAvailable(locale) >= TextToSpeech.LANG_AVAILABLE
        if (!supported || tts.setLanguage(locale) < TextToSpeech.LANG_AVAILABLE) {
          val defaultVoice = tts.defaultVoice
          if (defaultVoice != null) tts.setVoice(defaultVoice) else tts.setLanguage(Locale.getDefault())
        }
      }
      val params = Bundle().apply {
        options.volume?.let { putFloat(TextToSpeech.Engine.KEY_PARAM_VOLUME, it.coerceIn(0.0f, 1.0f)) }
      }
      if (tts.speak(text, TextToSpeech.QUEUE_ADD, params, id) == TextToSpeech.ERROR) {
        failEngine("Speech engine rejected an utterance")
      }
    } catch (error: Exception) {
      failEngine(error.message ?: "Speech engine request failed")
    }
  }

  private fun listener(current: Long) = object : UtteranceProgressListener() {
    private fun deliver(id: String, event: String, error: String? = null, start: Int? = null, end: Int? = null) {
      handler.post {
        if (current != generation || id !in activeIds) return@post
        if (event == DONE || event == STOPPED || event == ERROR) activeIds.remove(id)
        if (event != BOUNDARY) Log.d(TAG, "$event; generation=$current; id=$id")
        sendEvent(event, Bundle().apply {
          putString("id", id)
          error?.let { putString("error", it) }
          start?.let { putInt("charIndex", it) }
          if (start != null && end != null) putInt("charLength", end - start)
        })
      }
    }
    override fun onStart(id: String) = deliver(id, STARTED)
    override fun onDone(id: String) = deliver(id, DONE)
    override fun onStop(id: String, interrupted: Boolean) = deliver(id, STOPPED)
    override fun onError(id: String) = deliver(id, ERROR, "Speech engine error")
    override fun onError(id: String, errorCode: Int) = deliver(id, ERROR, "Speech engine error: $errorCode")
    override fun onRangeStart(id: String, start: Int, end: Int, frame: Int) = deliver(id, BOUNDARY, start = start, end = end)
  }

  private fun stopSpeech() {
    pendingSpeech.clear()
    val ids = activeIds.toList()
    activeIds.clear()
    engine?.stop()
    ids.forEach { sendEvent(STOPPED, mapOf("id" to it)) }
  }

  private fun failEngine(message: String) {
    Log.w(TAG, message)
    val ids = activeIds.toList()
    activeIds.clear()
    retire(message)
    ids.forEach { sendEvent(ERROR, mapOf("id" to it, "error" to message)) }
  }

  private fun retire(reason: String) {
    generation += 1
    ready = false
    val previous = engine
    engine = null
    pendingSpeech.clear()
    val ids = activeIds.toList()
    activeIds.clear()
    val requests = pendingVoices.toList()
    pendingVoices.clear()
    val engineRequests = pendingEngines.toList()
    pendingEngines.clear()
    engineRequests.forEach { it.reject("ERR_SPEECH_RESET", reason, null) }
    requests.forEach { it.reject("ERR_SPEECH_RESET", reason, null) }
    ids.forEach { sendEvent(STOPPED, mapOf("id" to it)) }
    previous?.shutdown()
  }

  private data class Utterance(val id: String, val text: String, val options: SpeechOptions)

  private data class EngineRecord(
    @Field val identifier: String,
    @Field val label: String,
    @Field val isDefault: Boolean,
    @Field val isSystem: Boolean
  ) : Record
}
