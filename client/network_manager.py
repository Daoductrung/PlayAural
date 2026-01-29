"""Network manager for WebSocket communication with server."""

import asyncio
import json
import threading
import wx
import websockets
import ssl


class NetworkManager:
    """Manages WebSocket connection to PlayAural server."""

    def __init__(self, main_window):
        """
        Initialize network manager.

        Args:
            main_window: Reference to MainWindow for callbacks
        """
        self.main_window = main_window
        self.ws = None
        self.connected = False
        self.connecting = False
        self.username = None
        self.thread = None
        self.loop = None
        self.should_stop = False

    def is_connecting(self):
        """Check if a connection attempt is in progress."""
        return self.connecting or (self.thread and self.thread.is_alive())

    def connect(self, server_url, username, password, client_version="0.0.0"):
        """
        Connect to server.
        
        Args:
            server_url: WebSocket URL (e.g., "wss://playaural.ddt.one")
            username: Username for authorization
            password: Password for authorization
            client_version: Version string of the client
        """
        try:
            # Prevent multiple concurrent connection attempts
            if self.is_connecting():
                return False

            # Wait for old thread to finish if it exists
            if self.thread and self.thread.is_alive():
                self.should_stop = True
                # Wait up to 2 seconds for thread to finish
                self.thread.join(timeout=2.0)

            self.username = username
            self.should_stop = False
            self.connecting = True

            # Start async thread
            self.thread = threading.Thread(
                target=self._run_async_loop,
                args=(server_url, username, password, client_version),
                daemon=True,
            )
            self.thread.start()

            return True
        except Exception:
            import traceback

            traceback.print_exc()
            self.connecting = False
            return False

    def _run_async_loop(self, server_url, username, password, client_version):
        """Run the async event loop in a thread."""
        try:
            # Create new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # Run the connection coroutine
            self.loop.run_until_complete(
                self._connect_and_listen(server_url, username, password, client_version)
            )
        except Exception:
            import traceback

            traceback.print_exc()
        finally:
            self.connecting = False
            if self.loop and self.loop.is_running():
                 self.loop.close()
            elif self.loop:
                 self.loop.close()

    async def _connect_and_listen(self, server_url, username, password, client_version):
        """Connect to server and listen for messages."""
        try:
            # Create SSL context that allows self-signed certificates
            ssl_context = None
            if server_url.startswith("wss://"):
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

            async with websockets.connect(server_url, ssl=ssl_context) as websocket:
                self.ws = websocket
                self.connected = True

                # Send authorization packet
                await websocket.send(
                    json.dumps(
                        {
                            "type": "authorize",
                            "username": username,
                            "password": password,
                            "version": client_version,
                        }
                    )
                )

                # Listen for messages
                while not self.should_stop:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        packet = json.loads(message)

                        # Forward to main thread
                        wx.CallAfter(self._handle_packet, packet)
                    except asyncio.TimeoutError:
                        # Timeout is normal, just continue
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        break

        except (ConnectionRefusedError, OSError, asyncio.TimeoutError) as e:
            # Common connection errors - log briefly, don't spam traceback
            # [WinError 1225] is an OSError
            print(f"Connection attempt failed: {e}")
        except Exception:
            import traceback

            traceback.print_exc()
        finally:
            self.connected = False
            self.ws = None
            # Only call on_connection_lost if we're not in the middle of stopping
            # (to avoid race conditions during reconnection)
            if not self.should_stop:
                wx.CallAfter(self.main_window.on_connection_lost)

    def disconnect(self):
        """Disconnect from server."""
        self.should_stop = True
        self.connected = False

        # Close websocket if it exists
        if self.ws and self.loop:
            try:
                # Schedule close in the async loop
                asyncio.run_coroutine_threadsafe(self.ws.close(), self.loop)
            except Exception:
                pass  # Ignore errors during cleanup

    def send_packet(self, packet):
        """
        Send packet to server.

        Args:
            packet: Dictionary to send as JSON
        """
        if not self.connected or not self.ws or not self.loop:
            return False

        try:
            message = json.dumps(packet)

            # Schedule send in the async loop
            asyncio.run_coroutine_threadsafe(self.ws.send(message), self.loop)
            return True
        except Exception:
            import traceback

            traceback.print_exc()
            self.connected = False
            wx.CallAfter(self.main_window.on_connection_lost)
            return False

    def _handle_packet(self, packet):
        """
        Handle incoming packet from server (called in main thread).

        Args:
            packet: Dictionary received from server
        """
        packet_type = packet.get("type")

        if packet_type == "update_locale":
             self.main_window.on_update_locale(packet)
        elif packet_type == "authorize_success":
            self.main_window.on_authorize_success(packet)
        elif packet_type == "speak":
            self.main_window.on_server_speak(packet)
        elif packet_type == "play_sound":
            self.main_window.on_server_play_sound(packet)
        elif packet_type == "play_music":
            self.main_window.on_server_play_music(packet)
        elif packet_type == "play_ambience":
            self.main_window.on_server_play_ambience(packet)
        elif packet_type == "stop_ambience":
            self.main_window.on_server_stop_ambience(packet)
        elif packet_type == "add_playlist":
            self.main_window.on_server_add_playlist(packet)
        elif packet_type == "start_playlist":
            self.main_window.on_server_start_playlist(packet)
        elif packet_type == "remove_playlist":
            self.main_window.on_server_remove_playlist(packet)
        elif packet_type == "get_playlist_duration":
            self.main_window.on_server_get_playlist_duration(packet)
        elif packet_type == "menu":
            self.main_window.on_server_menu(packet)
        elif packet_type == "request_input":
            self.main_window.on_server_request_input(packet)
        elif packet_type == "clear_ui":
            self.main_window.on_server_clear_ui(packet)
        elif packet_type == "game_list":
            self.main_window.on_server_game_list(packet)
        elif packet_type == "disconnect":
            self.main_window.on_server_disconnect(packet)
        elif packet_type == "update_options_lists":
            self.main_window.on_update_options_lists(packet)
        elif packet_type == "open_client_options":
            self.main_window.on_open_client_options(packet)
        elif packet_type == "open_server_options":
            self.main_window.on_open_server_options(packet)
        elif packet_type == "table_create":
            self.main_window.on_table_create(packet)
        elif packet_type == "chat":
            self.main_window.on_receive_chat(packet)
        elif packet_type == "force_exit":
             self.main_window.on_force_exit(packet)
        elif packet_type == "update_preference":
             self.main_window.on_update_preference(packet)
        elif packet_type == "pong":
            self.main_window.on_server_pong(packet)
