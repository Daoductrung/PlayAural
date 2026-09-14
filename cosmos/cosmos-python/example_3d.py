"""3D audio navigation example.

Controls:
  Arrow keys: Move forward/back/left/right (relative to facing direction)
  U/D: Move up/down
  Q/E: Turn left/right (45 degree increments)
  Shift+Up/Down: Increase/decrease pitch
  C: Speak current coordinates
  Escape: Quit
"""

import os
import sys
import math

# Set up library path before importing cosmos
#sys.path.insert(0, os.path.dirname(__file__))
#os.environ["COSMOS_LIB_PATH"] = os.path.dirname(os.path.dirname(__file__))

import cosmos


def main():

    # Create window and audio
    window = cosmos.Window("3D Audio Demo - Use arrows, U/D, Q/E")
    manager = cosmos.SoundManager()
    sr = cosmos.ScreenReader()

    # Listener state
    listener_x = 5.0
    listener_y = 5.0
    listener_z = 0.0
    listener_angle = 90.0  # Facing +Y (north) - unit circle convention

    # Set initial listener position
    manager.set_listener(listener_x, listener_y, listener_z, listener_angle)

    # Load and play music as a ranged sound from (0,0,0) to (3,3,0)
    music = manager.create_sound()
    music_file="mainmus.ogg"

    if not music.load(music_file):
        print(f"Failed to load {music_file}")
        return

    # Set as ranged sound: (minx, maxx, miny, maxy, minz, maxz)
    music.set_position_ranged(0, 3, 0, 3, 0, 0)
    music.looping = True
    music.hrtf = manager.hrtf_available  # Use HRTF if available
    music.play()

    print("3D Audio Demo")
    print("=============")
    print("Music playing as ranged sound from (0, 0, 0) to (3, 3, 0)")
    print(f"HRTF enabled: {music.hrtf}")
    print()
    print("Controls:")
    print("  Up/Down: Move forward/backward")
    print("  Left/Right: Strafe left/right")
    print("  U/D: Move up/down")
    print("  Q/E: Turn left/right (45 degrees)")
    print("  Shift+Up/Down: Increase/decrease pitch")
    print("  C: Speak current coordinates")
    print("  Escape: Quit")
    print()

    if sr.can_speak:
        sr.speak("3D audio demo. Use arrow keys to move, Q and E to turn.")

    move_speed = 1.0
    turn_amount = 45.0

    while window.is_open:
        window.update()

        moved = False
        turned = False

        # Quit
        if window.key_pressed(cosmos.Key.ESCAPE):
            window.close()
            continue

        # Calculate forward and right vectors based on facing angle
        angle_rad = math.radians(listener_angle)
        forward_x = math.cos(angle_rad)
        forward_y = math.sin(angle_rad)
        right_x = math.cos(angle_rad - math.radians(90))
        right_y = math.sin(angle_rad - math.radians(90))

        # Check if shift is held
        shift_held = window.key_held(cosmos.Key.LSHIFT) or window.key_held(cosmos.Key.RSHIFT)

        # Pitch control (Shift + Up/Down)
        if shift_held:
            if window.key_pressed(cosmos.Key.UP):
                music.pitch = min(music.pitch + 0.1, 3.0)
                print(f"Pitch: {music.pitch:.1f}")
            if window.key_pressed(cosmos.Key.DOWN):
                music.pitch = max(music.pitch - 0.1, 0.1)
                print(f"Pitch: {music.pitch:.1f}")
        else:
            # Movement (relative to facing direction)
            if window.key_pressed(cosmos.Key.UP):
                listener_x += forward_x * move_speed
                listener_y += forward_y * move_speed
                moved = True

            if window.key_pressed(cosmos.Key.DOWN):
                listener_x -= forward_x * move_speed
                listener_y -= forward_y * move_speed
                moved = True

        if window.key_pressed(cosmos.Key.LEFT):
            listener_x -= right_x * move_speed
            listener_y -= right_y * move_speed
            moved = True

        if window.key_pressed(cosmos.Key.RIGHT):
            listener_x += right_x * move_speed
            listener_y += right_y * move_speed
            moved = True

        if window.key_pressed(cosmos.Key.U):
            listener_z += move_speed
            moved = True

        if window.key_pressed(cosmos.Key.D):
            listener_z -= move_speed
            moved = True

        # Turning
        if window.key_pressed(cosmos.Key.Q):
            listener_angle += turn_amount  # Turn left (counter-clockwise)
            if listener_angle >= 360:
                listener_angle -= 360
            turned = True

        if window.key_pressed(cosmos.Key.E):
            listener_angle -= turn_amount  # Turn right (clockwise)
            if listener_angle < 0:
                listener_angle += 360
            turned = True

        # Speak coordinates
        if window.key_pressed(cosmos.Key.C):
            coords = f"{listener_x:.0f}, {listener_y:.0f}, {listener_z:.0f}"
            print(f"Coordinates: ({coords})")
            if sr.can_speak:
                sr.speak(coords)

        # Update listener if moved or turned
        if moved or turned:
            manager.set_listener(listener_x, listener_y, listener_z, listener_angle)

            # Calculate distance to sound
            dist = math.sqrt(listener_x**2 + listener_y**2 + listener_z**2)

            # Get compass direction
            directions = ["East", "Northeast", "North", "Northwest",
                         "West", "Southwest", "South", "Southeast"]
            dir_index = int((listener_angle + 22.5) // 45) % 8
            facing = directions[dir_index]

            status = f"Position: ({listener_x:.0f}, {listener_y:.0f}, {listener_z:.0f}) | Facing: {facing} ({listener_angle:.0f} deg) | Distance: {dist:.1f}"
            print(status)

            if sr.can_speak and turned:
                sr.speak(facing)

    # Cleanup
    music.stop()
    manager.destroy()
    window.destroy()
    print("Done!")


if __name__ == "__main__":
    main()
