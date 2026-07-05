"""Mixin providing lobby action handlers for games."""

import secrets
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..users.base import User

from ..users.base import MenuItem, EscapeBehavior
from ..users.bot import Bot
from ..messages.localization import Localization
from .player import Player
from .teams import TeamManager
from .bot_names import (
    generate_unique_bot_name,
    get_valid_bot_name_pool,
    normalize_bot_name,
    validate_custom_bot_name,
)


class LobbyActionsMixin:
    """Mixin providing lobby action handlers and player/lifecycle management.

    Expects on the Game class:
        - self.status: str
        - self.host: str
        - self.players: list[Player]
        - self._table: Any
        - self._users: dict
        - self._destroyed: bool
        - self._actions_menu_open: set[str]
        - self.player_action_sets: dict
        - self.get_user(player) -> User | None
        - self.broadcast_l(), self.broadcast_sound()
        - self.validate_start(), self.on_start()
        - self.attach_user(), self.refresh_menus()
        - self.get_all_enabled_actions()
        - self._get_keybind_for_action()
        - self.setup_keybinds(), self.setup_player_actions()
    """

    def _action_start_game(self, player: "Player", action_id: str) -> None:
        """Start the game."""
        if self.team_arrangement_active:
            self._action_confirm_team_arrangement(player, action_id)
            return

        # Validate framework requirements and game-specific configuration.
        errors = self.validate_start()
        if errors:
            self._broadcast_start_errors(errors)
            return

        self._prepare_disconnected_lobby_members_for_start()

        if self._should_begin_team_arrangement():
            self._begin_team_arrangement()
            return

        self._start_game_from_lobby()

    def _start_game_from_lobby(self) -> None:
        """Start gameplay after all lobby-only preparation has completed."""
        if hasattr(self, "_dismiss_all_end_screens"):
            self._dismiss_all_end_screens()
        self.broadcast_l("game-starting", buffer="system")
        self.on_start()
        self._focus_initial_gameplay_menu_items()
        self._clear_team_arrangement_state()
        self._sync_table_status()

    def _focus_initial_gameplay_menu_items(self) -> None:
        """Queue a one-shot focus reset to the first active menu row.

        The waiting lobby and active game both use ``turn_menu``. Without an
        explicit start-of-game focus directive, clients correctly preserve a
        surviving lobby utility such as ``whos_at_table`` into the first active
        menu. At the exact lobby->playing transition, the more useful landing
        is the first rendered gameplay row (cards, board cells, or primary
        actions). Mid-game refreshes continue to use normal client restoration.
        """
        if self.status != "playing":
            return

        for player in self.players:
            if player.is_bot:
                continue

            user = self.get_user(player)
            if not user:
                continue

            self.before_menu_build(player)
            build = self.build_menu_items(player, user)
            for item in build.items:
                item_id = getattr(item, "id", None)
                if item_id:
                    self.request_menu_focus(player, item_id)
                    break

    def _broadcast_start_errors(
        self,
        errors: list[str | tuple[str, dict]],
    ) -> None:
        """Announce every contextual reason the current setup cannot start."""
        for error in errors:
            if isinstance(error, tuple):
                error_key, kwargs = error
                self.broadcast_l(error_key, buffer="game", **kwargs)
            else:
                self.broadcast_l(error, buffer="game")

    def _prepare_disconnected_lobby_members_for_start(self) -> bool:
        """Convert offline lobby players to bots before game-specific setup."""
        table = self._table
        server = getattr(table, "_server", None) if table else None
        online_users = getattr(server, "_users", {}) if server else {}
        if not table or not server:
            return False

        changed = False
        for member in list(table.members):
            user = table._users.get(member.username)
            if member.username in online_users:
                table._member_offline_since.pop(member.username, None)
                continue
            if user and getattr(user, "is_bot", False):
                continue

            if member.is_spectator:
                player = self.get_player_by_id(user.uuid) if user else None
                if player:
                    self.remove_spectator(player.id)
                    self.play_table_leave_sound(player, is_spectator=True)
                table.remove_member(
                    member.username,
                    voice_reason="voice-status-connection-lost",
                )
                changed = True
                continue

            player = self.get_player_by_id(user.uuid) if user else None
            if not player:
                player = next(
                    (
                        current_player
                        for current_player in self.players
                        if current_player.name == member.username
                        and not current_player.is_bot
                    ),
                    None,
                )
            if (
                player
                and not player.is_bot
                and self._replace_with_bot(player, allow_waiting=True)
            ):
                self.play_table_leave_sound(
                    player,
                    is_bot=False,
                    is_spectator=False,
                )
                changed = True

        return changed

    # Team arrangement

    def allows_team_arrangement(self) -> bool:
        """Return whether this game allows host-controlled team arrangement."""
        return True

    def _configured_team_mode(self) -> str:
        """Return the currently selected team mode, if this game has one."""
        options = getattr(self, "options", None)
        return getattr(options, "team_mode", "individual")

    def _should_begin_team_arrangement(self) -> bool:
        """Return whether start should enter team arrangement instead of play."""
        team_mode = self._configured_team_mode()
        if team_mode == "individual":
            return False
        if not self.allows_team_arrangement():
            return False
        return TeamManager.is_valid_team_mode(team_mode, self.get_active_player_count())

    def _begin_team_arrangement(self) -> None:
        """Pre-assign teams and let the host confirm or swap members."""
        active_players = self.get_active_players()
        self.team_arrangement_active = True
        self.team_arrangement_selected_player_id = ""
        self.team_arrangement_team_mode = self._configured_team_mode()
        self._team_manager.team_mode = self.team_arrangement_team_mode
        self._team_manager.setup_teams([player.name for player in active_players])
        self._apply_team_indexes_from_manager()

        self.broadcast_l("team-arrangement-started", buffer="system")
        self._broadcast_team_arrangement()
        self.refresh_menus()

    def _clear_team_arrangement_state(self) -> None:
        """Clear transient team-arrangement UI state."""
        self.team_arrangement_active = False
        self.team_arrangement_selected_player_id = ""
        self.team_arrangement_team_mode = ""

    def _cancel_team_arrangement(self, message_key: str | None = None) -> None:
        """Cancel an active team-arrangement phase."""
        if not self.team_arrangement_active:
            return
        self._clear_team_arrangement_state()
        self._team_manager.teams = []
        self._team_manager._player_to_team = {}
        if message_key:
            self.broadcast_l(message_key, buffer="system")
        self.refresh_menus()

    def _cancel_team_arrangement_for_roster_change(self) -> None:
        """Cancel arrangement when active players change before confirmation."""
        self._cancel_team_arrangement("team-arrangement-cancelled-roster")

    def _active_player_names(self) -> list[str]:
        """Return current active player names in table order."""
        return [player.name for player in self.get_active_players()]

    def _team_arrangement_is_valid(self) -> bool:
        """Return whether the arranged teams still match the active roster."""
        if not self.team_arrangement_active:
            return False
        if self._configured_team_mode() != self.team_arrangement_team_mode:
            return False
        if self._team_manager.team_mode != self.team_arrangement_team_mode:
            return False
        return self._team_manager.validate_assignments(self._active_player_names())

    def _setup_team_manager_for_start(
        self,
        team_mode: str,
        active_players: list["Player"] | None = None,
    ) -> None:
        """Set up or reuse TeamManager assignments for game start."""
        active_players = (
            active_players if active_players is not None else self.get_active_players()
        )
        player_names = [player.name for player in active_players]
        self._team_manager.team_mode = team_mode

        if (
            self.team_arrangement_active
            and self.team_arrangement_team_mode == team_mode
            and self._team_manager.validate_assignments(player_names)
        ):
            self._team_manager.rebuild_player_index()
        else:
            self._team_manager.setup_teams(player_names)

        self._apply_team_indexes_from_manager(active_players)

    def _apply_team_indexes_from_manager(
        self,
        active_players: list["Player"] | None = None,
    ) -> None:
        """Mirror TeamManager assignment onto players with a team_index field."""
        active_players = (
            active_players if active_players is not None else self.get_active_players()
        )
        for current_player in active_players:
            team = self._team_manager.get_team(current_player.name)
            if team and hasattr(current_player, "team_index"):
                current_player.team_index = team.index

    def _rename_team_member(self, old_name: str, new_name: str) -> None:
        """Keep team assignments aligned with a player display-name change."""
        if self._team_manager.rename_member(old_name, new_name):
            self._apply_team_indexes_from_manager()

    def _sync_replacement_team_members(self) -> bool:
        """Repair team member names for seats currently held by replacement bots."""
        if not self._team_manager.teams:
            return False

        changed = False
        for current_player in self.get_active_players():
            replaced_human_name = getattr(current_player, "replaced_human_name", "")
            if (
                not replaced_human_name
                or replaced_human_name == current_player.name
                or self._team_manager.get_team(current_player.name)
            ):
                continue
            if self._team_manager.rename_member(
                replaced_human_name,
                current_player.name,
            ):
                changed = True

        if changed:
            self._apply_team_indexes_from_manager()
        return changed

    def _on_replacement_slot_reclaimed(self, bot_name: str, human_name: str) -> None:
        """Update team state after a human reclaims a bot-held seat."""
        self._rename_team_member(bot_name, human_name)
        if self.team_arrangement_active:
            self._broadcast_team_arrangement()

    def _get_team_turn_players(
        self,
        active_players: list["Player"] | None = None,
    ) -> list["Player"]:
        """Return active players in a team-balanced turn order."""
        active_players = (
            active_players if active_players is not None else self.get_active_players()
        )
        players_by_name = {
            current_player.name: current_player for current_player in active_players
        }
        ordered_names = self._team_manager.balanced_turn_order(
            [current_player.name for current_player in active_players]
        )
        ordered_players = [
            players_by_name[name] for name in ordered_names if name in players_by_name
        ]
        return ordered_players or active_players

    def _team_arrangement_lines(self, locale: str) -> list[str]:
        """Format the current team arrangement as localized lines."""
        lines: list[str] = []
        for team in sorted(self._team_manager.teams, key=lambda item: item.index):
            team_name = self._team_manager.get_team_name(team, locale)
            members = Localization.format_list_and(locale, team.members)
            lines.append(
                Localization.get(
                    locale,
                    "team-arrangement-line",
                    team=team_name,
                    members=members,
                )
            )
        turn_order = [player.name for player in self._get_team_turn_players()]
        if turn_order:
            lines.append(
                Localization.get(
                    locale,
                    "team-arrangement-turn-order",
                    players=Localization.format_list_and(locale, turn_order),
                )
            )
        return lines

    def _broadcast_team_arrangement(self) -> None:
        """Broadcast current team assignments line by line."""
        for current_player in self.players:
            user = self.get_user(current_player)
            if not user:
                continue
            for line in self._team_arrangement_lines(user.locale):
                user.speak(line, buffer="system")

    def _find_team_arrangement_player(self, player_id: str) -> "Player | None":
        """Find an active player by id for team arrangement."""
        for current_player in self.get_active_players():
            if current_player.id == player_id:
                return current_player
        return None

    def _team_arrangement_member_options(self, player: "Player") -> list[str]:
        """Return active player ids for the team-arrangement selection menu."""
        return [current_player.id for current_player in self.get_active_players()]

    def _team_arrangement_swap_options(self, player: "Player") -> list[str]:
        """Return candidate player ids for swapping with the selected member."""
        selected_id = self.team_arrangement_selected_player_id
        selected = self._find_team_arrangement_player(selected_id)
        selected_team = self._team_manager.get_team(selected.name) if selected else None
        options: list[str] = []
        for current_player in self.get_active_players():
            if current_player.id == selected_id:
                continue
            candidate_team = self._team_manager.get_team(current_player.name)
            if (
                selected_team
                and candidate_team
                and candidate_team.index == selected_team.index
            ):
                continue
            options.append(current_player.id)
        return options

    def _team_arrangement_member_label(self, player: "Player", target_id: str) -> str:
        """Return a localized label for a selectable team member."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        target = self._find_team_arrangement_player(target_id)
        if not target:
            return target_id
        team = self._team_manager.get_team(target.name)
        team_name = (
            self._team_manager.get_team_name(team, locale)
            if team
            else Localization.get(locale, "game-team-name", index=0)
        )
        selected_key = (
            "team-arrangement-selected"
            if target.id == self.team_arrangement_selected_player_id
            else "team-arrangement-not-selected"
        )
        return Localization.get(
            locale,
            "team-arrangement-member-option",
            player=target.name,
            team=team_name,
            selected=Localization.get(locale, selected_key),
        )

    def _team_arrangement_swap_label(self, player: "Player", target_id: str) -> str:
        """Return a localized label for a swap target."""
        return self._team_arrangement_member_label(player, target_id)

    def _get_swap_team_member_label(self, player: "Player", action_id: str) -> str:
        """Return the swap action label, including selected player when present."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        selected = self._find_team_arrangement_player(
            self.team_arrangement_selected_player_id
        )
        if not selected:
            return Localization.get(locale, "team-arrangement-swap-member")
        return Localization.get(
            locale,
            "team-arrangement-swap-member-selected",
            player=selected.name,
        )

    def _action_confirm_team_arrangement(
        self, player: "Player", action_id: str
    ) -> None:
        """Confirm arranged teams and start the game."""
        if player.name != self.host or not self.team_arrangement_active:
            return

        errors = self.validate_start()
        if errors:
            self._broadcast_start_errors(errors)
            return

        roster_changed = self._prepare_disconnected_lobby_members_for_start()
        if not self._should_begin_team_arrangement():
            self._start_game_from_lobby()
            return

        if roster_changed or not self._team_arrangement_is_valid():
            self.broadcast_l("team-arrangement-refreshed", buffer="system")
            self._begin_team_arrangement()
            return

        self._start_game_from_lobby()

    def _action_cancel_team_arrangement(
        self, player: "Player", action_id: str
    ) -> None:
        """Cancel arranged teams and return to normal lobby setup."""
        if player.name != self.host:
            return
        self._cancel_team_arrangement("team-arrangement-cancelled")

    def _action_read_team_arrangement(self, player: "Player", action_id: str) -> None:
        """Read the current team arrangement to one player."""
        user = self.get_user(player)
        if not user:
            return
        if not self.team_arrangement_active:
            user.speak_l("team-arrangement-not-active", buffer="system")
            return
        for line in self._team_arrangement_lines(user.locale):
            user.speak(line, buffer="system")

    def _action_select_team_member(
        self, player: "Player", selected_id: str, action_id: str
    ) -> None:
        """Select a team member before choosing a swap target."""
        if player.name != self.host:
            return
        selected = self._find_team_arrangement_player(selected_id)
        user = self.get_user(player)
        if not selected:
            if user:
                user.speak_l("team-arrangement-player-missing", buffer="system")
            return

        self.team_arrangement_selected_player_id = selected.id
        team = self._team_manager.get_team(selected.name)
        locale = user.locale if user else "en"
        team_name = (
            self._team_manager.get_team_name(team, locale)
            if team
            else Localization.get(locale, "game-team-name", index=0)
        )
        if user:
            user.speak_l(
                "team-arrangement-member-selected",
                buffer="system",
                player=selected.name,
                team=team_name,
            )
        self.refresh_menus()

    def _action_swap_team_member(
        self, player: "Player", target_id: str, action_id: str
    ) -> None:
        """Swap the selected team member with another active player."""
        if player.name != self.host:
            return

        user = self.get_user(player)
        selected = self._find_team_arrangement_player(
            self.team_arrangement_selected_player_id
        )
        target = self._find_team_arrangement_player(target_id)
        if not selected or not target:
            if user:
                user.speak_l("team-arrangement-player-missing", buffer="system")
            self.team_arrangement_selected_player_id = ""
            self.refresh_menus()
            return

        selected_team = self._team_manager.get_team(selected.name)
        target_team = self._team_manager.get_team(target.name)
        if selected_team and target_team and selected_team.index == target_team.index:
            if user:
                user.speak_l("team-arrangement-same-team", buffer="system")
            return

        if not self._team_manager.swap_members(selected.name, target.name):
            if user:
                user.speak_l("team-arrangement-swap-failed", buffer="system")
            return

        self._apply_team_indexes_from_manager()
        self.team_arrangement_selected_player_id = ""
        self.broadcast_l(
            "team-arrangement-swapped",
            buffer="system",
            first=selected.name,
            second=target.name,
        )
        self._broadcast_team_arrangement()
        self.refresh_menus()

    def _bot_input_add_bot(self, player: "Player") -> str | None:
        """Get bot name for add_bot action."""
        return self._generate_available_bot_name()

    def _should_prompt_add_bot(self, player: "Player") -> bool:
        """Return whether the host wants to type custom bot names."""
        user = self.get_user(player)
        return bool(user and user.preferences.allow_custom_bot_names)

    def _existing_player_names(self) -> list[str]:
        """Return every current table player/spectator display name."""
        if self._table and hasattr(self._table, "reserved_names"):
            return self._table.reserved_names()

        names: list[str] = []
        for current_player in self.players:
            names.append(current_player.name)
            replaced_name = getattr(current_player, "replaced_human_name", "")
            if replaced_name:
                names.append(replaced_name)
        return names

    def _is_registered_username(self, name: str) -> bool:
        """Return whether a bot name matches an existing account name."""
        server = getattr(self._table, "_server", None) if self._table else None
        db = getattr(server, "_db", None)
        return bool(db and db.get_user(name))

    def _generate_available_bot_name(self, existing_names: list[str] | None = None) -> str:
        """Generate a bot name that avoids table names and registered accounts."""
        existing_names = (
            list(existing_names) if existing_names is not None else self._existing_player_names()
        )
        max_attempts = len(get_valid_bot_name_pool()) * 100
        for _ in range(max_attempts):
            bot_name = generate_unique_bot_name(existing_names)
            if not self._is_registered_username(bot_name):
                return bot_name
            existing_names.append(bot_name)
        return self._generate_emergency_bot_name(existing_names)

    def _generate_emergency_bot_name(self, existing_names: list[str]) -> str:
        """Generate a non-pool bot name if every configured bot name is unavailable."""
        for _ in range(1000):
            bot_name = f"Bot {secrets.randbelow(1_000_000):06d}"
            if validate_custom_bot_name(bot_name, existing_names) is not None:
                continue
            if self._is_registered_username(bot_name):
                existing_names.append(bot_name)
                continue
            return bot_name
        raise RuntimeError("Unable to generate an unregistered bot name")

    def _resolve_add_bot_name(
        self,
        player: "Player",
        requested_name: str,
    ) -> str | None:
        """Resolve and validate the bot name for the add_bot action."""
        if self._should_prompt_add_bot(player):
            bot_name = normalize_bot_name(requested_name)
            error_key = validate_custom_bot_name(
                bot_name,
                self._existing_player_names(),
            )
            if error_key:
                user = self.get_user(player)
                if user:
                    user.speak_l(error_key, buffer="game")
                return None
            if self._is_registered_username(bot_name):
                user = self.get_user(player)
                if user:
                    user.speak_l("bot-name-registered-account", buffer="game")
                return None
            return bot_name

        return self._generate_available_bot_name()

    def _action_add_bot(self, player: "Player", bot_name: str, action_id: str) -> None:
        """Add a bot with the selected name."""
        if self.team_arrangement_active:
            return

        bot_name = self._resolve_add_bot_name(player, bot_name)
        if bot_name is None:
            return

        bot_user = Bot(bot_name)
        bot_player = self.create_player(bot_user.uuid, bot_name, is_bot=True)
        self.players.append(bot_player)
        self.attach_user(bot_player.id, bot_user)
        # Set up action sets for the bot
        self.setup_player_actions(bot_player)
        self.broadcast_l("table-joined", buffer="system", player=bot_name)
        self.play_table_join_sound(bot_player, is_bot=True)
        self.refresh_menus()
        self._notify_table_presence_changed()

    def _action_remove_bot(self, player: "Player", action_id: str) -> None:
        """Remove the last bot from the game."""
        if self.team_arrangement_active:
            return

        for i in range(len(self.players) - 1, -1, -1):
            if self.players[i].is_bot:
                bot = self.players.pop(i)
                # Clean up action sets
                self.player_action_sets.pop(bot.id, None)
                self._users.pop(bot.id, None)
                self.broadcast_l("table-left", buffer="system", player=bot.name)
                self.play_table_leave_sound(bot, is_bot=True)
                break
        self.refresh_menus()
        self._notify_table_presence_changed()

    def _action_toggle_spectator(self, player: "Player", action_id: str) -> None:
        """Toggle spectator mode for a player."""
        if self.status != "waiting":
            return  # Can only toggle before game starts
        if self.team_arrangement_active:
            return

        # If currently a spectator trying to become a player, check capacity
        if player.is_spectator:
            active_players = sum(1 for p in self.players if not p.is_spectator)
            if active_players >= self.get_max_players():
                user = self.get_user(player)
                if user:
                    user.speak_l("table-full", buffer="game")
                return

        player.is_spectator = not player.is_spectator
        
        # SYNC FIX: Update the table member record to match
        if self._table:
            for member in self._table.members:
                if member.username == player.name:
                    member.is_spectator = player.is_spectator
                    break
        
        if player.is_spectator:
            self.broadcast_l("now-spectating", buffer="system", player=player.name)
            self.broadcast_sound("join_spectator.ogg")
        else:
            self.broadcast_l("now-playing", buffer="system", player=player.name)
            self.broadcast_sound("leave_spectator.ogg")

        self.refresh_menus()
        self._notify_table_presence_changed()

    def _perform_leave_game(self, player: "Player") -> None:
        """Leave the game."""
        # Spectators can always leave cleanly (no bot replacement)
        if player.is_spectator:
            # BUGFIX: Ensure they are removed from the TABLE as well as the GAME
            # Use the new centralized helper for game state
            self.remove_spectator(player.id)
            
            # Explicitly remove from table to prevent ghost in lobby
            if self._table:
                self._table.remove_member(player.name)
                
            self.play_table_leave_sound(player, is_spectator=True)
            self.refresh_menus()
            return

        if self.status == "playing" and not player.is_bot:
            # Check if any humans remain (excluding spectators and current player)
            # We do this check FIRST to handle the "Last Human Leaves" case specially
            other_humans = any(not p.is_bot and not p.is_spectator and p.id != player.id for p in self.players)
            
            if other_humans:
                # Mid-game AND other humans exist: replace with bot
                was_bot = player.is_bot
                if self._replace_with_bot(player):
                    self.play_table_leave_sound(
                        player,
                        is_bot=was_bot,
                        is_spectator=False,
                    )
                self.refresh_menus()
                return

            # If no other humans, fall through to full removal logic below
            # This suppresses "replaced by bot" message and shows "left table" instead
            pass

        # Lobby or bot leaving: fully remove the player
        # Use centralized helper to ensure consistent cleanup
        was_bot = player.is_bot
        was_spectator = player.is_spectator
        self.remove_player(player.id)

        self.play_table_leave_sound(
            player,
            is_bot=was_bot,
            is_spectator=was_spectator,
        )

        # Check if any humans remain (excluding spectators)
        has_humans = any(not p.is_bot and not p.is_spectator for p in self.players)
        if not has_humans:
            # Destroy the game - no humans left
            self.destroy()
            return

        if self.status == "waiting":
            # Sync with table - this will trigger host promotion in Table.remove_member if needed
            if self._table:
                self._table.remove_member(player.name)

            self.refresh_menus()

    def _action_show_actions_menu(self, player: "Player", action_id: str) -> None:
        """Show the actions menu."""
        return_focus = self._get_action_return_focus_id(player, action_id)
        if return_focus:
            self._actions_menu_return_focus[player.id] = return_focus
        self._paint_actions_menu(player, announce=True)

    def _build_actions_menu_items(self, player: "Player", user: "User") -> list[MenuItem]:
        """Build the current Escape/actions menu for a player."""
        items = []
        for resolved in self.get_all_enabled_actions(player):
            label = resolved.label
            keybind_key = self._get_keybind_for_action(resolved.action.id)
            if keybind_key:
                label += f" ({keybind_key.upper()})"
            items.append(MenuItem(text=label, id=resolved.action.id))

        items.append(
            MenuItem(text=Localization.get(user.locale, "go-back"), id="go_back")
        )
        return items

    def _paint_actions_menu(
        self,
        player: "Player",
        *,
        focus_id: str | None = None,
        announce: bool = False,
    ) -> None:
        """Paint or refresh the actions menu without rebuilding the turn menu."""
        user = self.get_user(player)
        if not user:
            return

        items = self._build_actions_menu_items(player, user)
        action_ids = {item.id for item in items if item.id is not None}
        if focus_id not in action_ids:
            focus_id = None

        self._actions_menu_open.add(player.id)
        if announce:
            user.speak_l("context-menu", buffer="game")
            if len(items) == 1:
                user.speak_l("no-actions-available", buffer="game")

        user.show_menu(
            "actions_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
            selection_id=focus_id,
        )

    def _action_leave_game(self, player: "Player", action_id: str) -> None:
        """Prompt for confirmation before leaving the game."""
        user = self.get_user(player)
        if not user:
            return
        return_focus = self._get_action_return_focus_id(player, None)
        if return_focus:
            self._pending_action_return_focus[player.id] = return_focus
        self._pending_actions[player.id] = "leave_game_confirm"
        user.speak_l("confirm-leave-game", buffer="game")
        items = [
            MenuItem(text=Localization.get(user.locale, "confirm-no"), id="no"),
            MenuItem(text=Localization.get(user.locale, "confirm-yes"), id="yes"),
        ]
        user.show_menu(
            "leave_game_confirm",
            items,
            multiletter=False,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )

    def _action_host_management(self, player: "Player", action_id: str) -> None:
        """Open the server-level host management menu (host only)."""
        if player.name != self.host:
            return
        user = self.get_user(player)
        if not user or not self._table:
            return
        server = self._table._server
        if server and hasattr(server, "_open_host_management_from_game"):
            server._open_host_management_from_game(
                user,
                self._table,
                return_focus_id=self._get_action_return_focus_id(player, action_id),
            )

    def _action_save_table(self, player: "Player", action_id: str) -> None:
        """Save the current table state (host only). This destroys the table."""
        if self._table:
            self._table.save_and_close(player.name)

    # Game lifecycle

    def destroy(self) -> None:
        """Request destruction of this game/table."""
        self._destroyed = True
        
        # Cleanup game result (if GameResultMixin is present)
        if hasattr(self, "clear_last_game_result"):
            self.clear_last_game_result()
            
        if self._table:
            self._table.destroy()

    def initialize_lobby(self, host_name: str, host_user: "User") -> None:
        """Initialize the game in lobby mode with a host."""
        self.host = host_name
        self.status = "waiting"
        self.setup_keybinds()
        self.add_player(host_name, host_user)
        self.refresh_menus()

    # Player management

    def get_human_count(self) -> int:
        """Get the number of human players."""
        return sum(1 for p in self.players if not p.is_bot)

    def get_bot_count(self) -> int:
        """Get the number of bot players."""
        return sum(1 for p in self.players if p.is_bot)

    def create_player(
        self, player_id: str, name: str, is_bot: bool = False
    ) -> "Player":
        """Create a new player. Override in subclasses for custom player types."""
        return Player(id=player_id, name=name, is_bot=is_bot)

    def add_player(self, name: str, user: "User") -> "Player":
        """Add a player to the game."""
        is_bot = hasattr(user, "is_bot") and user.is_bot
        player = self.create_player(user.uuid, name, is_bot=is_bot)
        self.players.append(player)
        self.attach_user(player.id, user)
        # Set up action sets for the new player
        self.setup_player_actions(player)
        if self.team_arrangement_active and not player.is_spectator:
            self._cancel_team_arrangement_for_roster_change()
        self._notify_table_presence_changed()
        return player

    def add_spectator(self, name: str, user: "User") -> "Player":
        """Add a spectator to the game."""
        player = self.create_player(user.uuid, name, is_bot=False)
        player.is_spectator = True
        self.players.append(player)
        self.attach_user(player.id, user)
        self.setup_player_actions(player)
        self._notify_table_presence_changed()
        return player
