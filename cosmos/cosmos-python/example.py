"""Example script demonstrating the Rust-based Cosmos Python bindings."""

import cosmos
import time

def main():
    print("Cosmos Python Bindings Test")
    print("=" * 40)

    # Test SoundManager
    print("\n1. Testing SoundManager...")
    manager = cosmos.SoundManager()
    print(f"   HRTF available: {manager.hrtf_available}")

    # Test Sound
    print("\n2. Testing Sound...")
    sound = manager.create_sound()

    # Try loading the test audio file
    if sound.load("../mainmus.ogg"):
        print(f"   Sound loaded! Length: {sound.length} ms")
        sound.volume = 0.5
        sound.looping = True
        sound.hrtf = True
        sound.set_position(5.0, 0.0, 0.0)
        print(f"   Position: {sound.position}")
        print(f"   Volume: {sound.volume}")
        print(f"   HRTF: {sound.hrtf}")

        print("\n   Playing sound for 3 seconds...")
        sound.play()
        time.sleep(3)
        sound.stop()
        print("   Stopped.")
    else:
        print("   Could not load audio file (mainmus.ogg not found)")

    # Test ScreenReader
    print("\n3. Testing ScreenReader...")
    sr = cosmos.ScreenReader()
    print(f"   Can speak: {sr.can_speak}")
    if sr.can_speak:
        try:
            sr.speak("Hello from Rust Cosmos!")
            print("   Spoke: 'Hello from Rust Cosmos!'")
        except Exception as e:
            print(f"   Error speaking: {e}")

    # Test Key constants
    print("\n4. Testing Key constants...")
    print(f"   Key.A = {cosmos.Key.A}")
    print(f"   Key.SPACE = {cosmos.Key.SPACE}")
    print(f"   Key.ESCAPE = {cosmos.Key.ESCAPE}")
    print(f"   Key.UP = {cosmos.Key.UP}")

    print("\n" + "=" * 40)
    print("All tests completed!")

if __name__ == "__main__":
    main()
