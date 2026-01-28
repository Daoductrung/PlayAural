"""
Buffer System for PlayAural Client
Manages multiple message buffers with navigation and mute capabilities.
Ported from XG Legends buffer_system.lua
"""

import time
from typing import Dict, List, Set, Tuple, Optional


class BufferSystem:
    """Manages multiple message buffers for organizing game output."""

    def __init__(self):
        """Initialize the buffer system."""
        self.buffers: Dict[str, List[Dict]] = {}  # name -> list of message items
        self.buffer_order: List[str] = []  # ordered list of buffer names
        self.current_buffer_index: int = 0  # which buffer user is viewing (0-based)
        self.buffer_positions: Dict[str, int] = {}  # name -> position (0 = newest)
        self.muted_buffers: Set[str] = set()  # set of muted buffer names

    def create_buffer(self, name: str) -> None:
        """
        Create a new buffer.

        Args:
            name: Name of the buffer to create
        """
        if name not in self.buffers:
            self.buffers[name] = []
            self.buffer_order.append(name)
            self.buffer_positions[name] = 0

    def add_item(self, buffer_name: str, text: str) -> None:
        """
        Add a message to a specific buffer (and automatically to "all").

        Args:
            buffer_name: Name of the buffer to add to
            text: Message text to add
        """
        # Create buffer if it doesn't exist
        if buffer_name not in self.buffers:
            self.create_buffer(buffer_name)

        # Create message item
        item = {"text": text, "timestamp": time.time()}

        # Add to specified buffer
        self.buffers[buffer_name].append(item)

        # Also add to "all" buffer (unless this IS the "all" buffer)
        if buffer_name != "all" and "all" in self.buffers:
            self.buffers["all"].append(item)

    def next_buffer(self) -> None:
        """Switch to the next buffer in the list (does not wrap)."""
        if len(self.buffer_order) > 0:
            # Only increment if not already at the last buffer
            if self.current_buffer_index < len(self.buffer_order) - 1:
                self.current_buffer_index += 1

    def previous_buffer(self) -> None:
        """Switch to the previous buffer in the list (does not wrap)."""
        if len(self.buffer_order) > 0:
            # Only decrement if not already at the first buffer
            if self.current_buffer_index > 0:
                self.current_buffer_index -= 1

    def first_buffer(self) -> None:
        """Jump to the first buffer."""
        if len(self.buffer_order) > 0:
            self.current_buffer_index = 0

    def last_buffer(self) -> None:
        """Jump to the last buffer."""
        if len(self.buffer_order) > 0:
            self.current_buffer_index = len(self.buffer_order) - 1

    def get_current_buffer_name(self) -> str:
        """
        Get the name of the current buffer.

        Returns:
            Name of current buffer, or empty string if no buffers exist
        """
        if 0 <= self.current_buffer_index < len(self.buffer_order):
            return self.buffer_order[self.current_buffer_index]
        return ""

    def move_in_buffer(self, direction: str) -> None:
        """
        Navigate through messages in the current buffer.

        Args:
            direction: One of "older", "newer", "oldest", "newest"
        """
        buffer_name = self.get_current_buffer_name()
        if not buffer_name or buffer_name not in self.buffers:
            return

        buffer = self.buffers[buffer_name]
        buffer_size = len(buffer)
        current_position = self.buffer_positions.get(buffer_name, 0)

        if direction == "older":
            # Move back in history (increase position)
            if current_position < buffer_size - 1:
                self.buffer_positions[buffer_name] = current_position + 1

        elif direction == "newer":
            # Move forward in history (decrease position)
            if current_position > 0:
                self.buffer_positions[buffer_name] = current_position - 1

        elif direction == "oldest":
            # Jump to oldest message
            if buffer_size > 0:
                self.buffer_positions[buffer_name] = buffer_size - 1

        elif direction == "newest":
            # Jump to newest message
            self.buffer_positions[buffer_name] = 0

    def get_current_item(self) -> Optional[Dict]:
        """
        Get the message at the current position in the current buffer.

        Returns:
            Message item dict, or None if buffer is empty or invalid
        """
        buffer_name = self.get_current_buffer_name()
        if not buffer_name or buffer_name not in self.buffers:
            return None

        buffer = self.buffers[buffer_name]
        position = self.buffer_positions.get(buffer_name, 0)

        if len(buffer) == 0:
            return None

        # Position 0 = newest (last item in array)
        # Position increases as you go back in time
        index = len(buffer) - 1 - position

        if 0 <= index < len(buffer):
            return buffer[index]

        return None

    def get_buffer_info(self) -> Tuple[str, int, int]:
        """
        Get information about the current buffer.

        Returns:
            Tuple of (buffer_name, message_count, current_position)
        """
        buffer_name = self.get_current_buffer_name()
        if not buffer_name or buffer_name not in self.buffers:
            return ("", 0, 0)

        buffer = self.buffers[buffer_name]
        position = self.buffer_positions.get(buffer_name, 0)

        return (buffer_name, len(buffer), position)

    def toggle_mute(self, buffer_name: str) -> None:
        """
        Toggle mute status for a buffer.

        Args:
            buffer_name: Name of buffer to mute/unmute
        """
        if buffer_name in self.muted_buffers:
            self.muted_buffers.remove(buffer_name)
        else:
            self.muted_buffers.add(buffer_name)

    def is_muted(self, buffer_name: str) -> bool:
        """
        Check if a buffer is muted.

        Args:
            buffer_name: Name of buffer to check

        Returns:
            True if buffer is muted, False otherwise
        """
        return buffer_name in self.muted_buffers

    def get_muted_buffers(self) -> Set[str]:
        """
        Get the set of muted buffer names.

        Returns:
            Set of muted buffer names
        """
        return self.muted_buffers.copy()

    def clear_buffer(self, buffer_name: str) -> None:
        """
        Clear all messages from a specific buffer.

        Args:
            buffer_name: Name of buffer to clear
        """
        if buffer_name in self.buffers:
            self.buffers[buffer_name] = []
            self.buffer_positions[buffer_name] = 0

    def clear_all_buffers(self) -> None:
        """Clear all messages from all buffers."""
        for buffer_name in self.buffers:
            self.buffers[buffer_name] = []
            self.buffer_positions[buffer_name] = 0
