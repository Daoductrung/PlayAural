"""Administration functionality for the PlayAural server."""

import functools
import asyncio
from typing import TYPE_CHECKING

from ..users.network_user import NetworkUser
from ..users.base import MenuItem, EscapeBehavior
from ..messages.localization import Localization

if TYPE_CHECKING:
    from ..persistence.database import Database


def require_admin(func):
    """Decorator that checks if the user is still an admin before executing an admin action."""
    @functools.wraps(func)
    async def wrapper(self, admin, *args, **kwargs):
        if admin.trust_level < 2:
            admin.speak_l("not-admin-anymore")
            self._show_main_menu(admin)
            return
        return await func(self, admin, *args, **kwargs)
    return wrapper


class AdministrationMixin:
    """
    Mixin class providing administration functionality.

    This mixin expects the following attributes on the class it's mixed into:
    - _db: Database instance
    - _users: dict[str, NetworkUser] of online users
    - _user_states: dict[str, dict] of user menu states
    - _show_main_menu(user): method to show main menu
    """

    _db: "Database"
    _users: dict[str, NetworkUser]
    _user_states: dict[str, dict]

    def _show_main_menu(self, user: NetworkUser) -> None:
        """Show main menu - to be implemented by the main class."""
        raise NotImplementedError

    def _notify_admins(
        self, message_id: str, sound: str, exclude_username: str | None = None
    ) -> None:
        """Notify all online admins with a message and sound, optionally excluding one admin."""
        for username, user in self._users.items():
            if user.trust_level < 2:
                continue  # Not an admin
            if exclude_username and username == exclude_username:
                continue  # Skip the excluded admin
            user.speak_l(message_id)
            user.play_sound(sound)

    # ==================== Menu Display Functions ====================

    def _show_admin_menu(self, user: NetworkUser) -> None:
        """Show administration menu."""
        items = [
            MenuItem(
                text=Localization.get(user.locale, "account-approval"),
                id="account_approval",
            ),
            MenuItem(
                text=Localization.get(user.locale, "promote-admin"),
                id="promote_admin",
            ),
            MenuItem(
                text=Localization.get(user.locale, "demote-admin"),
                id="demote_admin",
            ),
            MenuItem(
                text=Localization.get(user.locale, "broadcast-announcement"),
                id="broadcast_announcement",
            ),
            MenuItem(
                text=Localization.get(user.locale, "kick-user"),
                id="kick_user",
            ),
            MenuItem(text=Localization.get(user.locale, "back"), id="back"),
        ]
        user.show_menu(
            "admin_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "admin_menu"}

    def _show_account_approval_menu(self, user: NetworkUser) -> None:
        """Show account approval menu with pending users."""
        pending = self._db.get_pending_users()

        if not pending:
            user.speak_l("no-pending-accounts")
            self._show_admin_menu(user)
            return

        items = []
        for pending_user in pending:
            items.append(MenuItem(text=pending_user.username, id=f"pending_{pending_user.username}"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "account_approval_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "account_approval_menu"}

    def _show_pending_user_actions_menu(self, user: NetworkUser, pending_username: str) -> None:
        """Show actions for a pending user (approve, decline)."""
        items = [
            MenuItem(text=Localization.get(user.locale, "approve-account"), id="approve"),
            MenuItem(text=Localization.get(user.locale, "decline-account"), id="decline"),
            MenuItem(text=Localization.get(user.locale, "back"), id="back"),
        ]
        user.show_menu(
            "pending_user_actions_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "pending_user_actions_menu",
            "pending_username": pending_username,
        }

    def _show_promote_admin_menu(self, user: NetworkUser) -> None:
        """Show promote admin menu with list of non-admin users."""
        non_admins = self._db.get_non_admin_users()

        if not non_admins:
            user.speak_l("no-users-to-promote")
            self._show_admin_menu(user)
            return

        items = []
        for non_admin in non_admins:
            items.append(MenuItem(text=non_admin.username, id=f"promote_{non_admin.username}"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "promote_admin_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "promote_admin_menu"}

    def _show_demote_admin_menu(self, user: NetworkUser) -> None:
        """Show demote admin menu with list of admin users."""
        admins = self._db.get_admin_users()

        # Filter out the current user (can't demote yourself) and developers (trust_level >= 3)
        admins = [a for a in admins if a.username != user.username and a.trust_level < 3]

        if not admins:
            user.speak_l("no-admins-to-demote")
            self._show_admin_menu(user)
            return

        items = []
        for admin in admins:
            items.append(MenuItem(text=admin.username, id=f"demote_{admin.username}"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "demote_admin_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "demote_admin_menu"}

    def _show_promote_confirm_menu(self, user: NetworkUser, target_username: str) -> None:
        """Show confirmation menu for promoting a user to admin."""
        user.speak_l("confirm-promote", player=target_username)
        items = [
            MenuItem(text=Localization.get(user.locale, "confirm-yes"), id="yes"),
            MenuItem(text=Localization.get(user.locale, "confirm-no"), id="no"),
        ]
        user.show_menu(
            "promote_confirm_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "promote_confirm_menu",
            "target_username": target_username,
        }

    def _show_demote_confirm_menu(self, user: NetworkUser, target_username: str) -> None:
        """Show confirmation menu for demoting an admin."""
        user.speak_l("confirm-demote", player=target_username)
        items = [
            MenuItem(text=Localization.get(user.locale, "confirm-yes"), id="yes"),
            MenuItem(text=Localization.get(user.locale, "confirm-no"), id="no"),
        ]
        user.show_menu(
            "demote_confirm_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "demote_confirm_menu",
            "target_username": target_username,
        }

    def _show_broadcast_choice_menu(self, user: NetworkUser, action: str, target_username: str) -> None:
        """Show menu to choose broadcast audience (all users, admins only, or nobody/silent)."""
        items = [
            MenuItem(text=Localization.get(user.locale, "broadcast-to-all"), id="all"),
            MenuItem(text=Localization.get(user.locale, "broadcast-to-admins"), id="admins"),
            MenuItem(text=Localization.get(user.locale, "broadcast-to-nobody"), id="nobody"),
        ]
        user.show_menu(
            "broadcast_choice_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "broadcast_choice_menu",
            "action": action,  # "promote" or "demote"
            "target_username": target_username,
        }

    # ==================== Menu Selection Handlers ====================

    async def _handle_admin_menu_selection(
        self, user: NetworkUser, selection_id: str
    ) -> None:
        """Handle admin menu selection."""
        if selection_id == "account_approval":
            self._show_account_approval_menu(user)
        elif selection_id == "promote_admin":
            self._show_promote_admin_menu(user)
        elif selection_id == "demote_admin":
            self._show_demote_admin_menu(user)
        elif selection_id == "kick_user":
            self._show_kick_menu(user)
        elif selection_id == "broadcast_announcement":
            self._show_broadcast_input_menu(user)
        elif selection_id == "back":
            self._show_main_menu(user)

    async def _handle_account_approval_selection(
        self, user: NetworkUser, selection_id: str
    ) -> None:
        """Handle account approval menu selection."""
        if selection_id == "back":
            self._show_admin_menu(user)
        elif selection_id.startswith("pending_"):
            pending_username = selection_id[8:]  # Remove "pending_" prefix
            self._show_pending_user_actions_menu(user, pending_username)

    async def _handle_pending_user_actions_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle pending user actions menu selection."""
        pending_username = state.get("pending_username")
        if not pending_username:
            self._show_account_approval_menu(user)
            return

        if selection_id == "approve":
            await self._approve_user(user, pending_username)
        elif selection_id == "decline":
            await self._decline_user(user, pending_username)
        elif selection_id == "back":
            self._show_account_approval_menu(user)

    async def _handle_promote_admin_selection(
        self, user: NetworkUser, selection_id: str
    ) -> None:
        """Handle promote admin menu selection."""
        if selection_id == "back":
            self._show_admin_menu(user)
        elif selection_id.startswith("promote_"):
            target_username = selection_id[8:]  # Remove "promote_" prefix
            self._show_promote_confirm_menu(user, target_username)

    async def _handle_demote_admin_selection(
        self, user: NetworkUser, selection_id: str
    ) -> None:
        """Handle demote admin menu selection."""
        if selection_id == "back":
            self._show_admin_menu(user)
        elif selection_id.startswith("demote_"):
            target_username = selection_id[7:]  # Remove "demote_" prefix
            self._show_demote_confirm_menu(user, target_username)

    async def _handle_promote_confirm_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle promote confirmation menu selection."""
        target_username = state.get("target_username")
        if not target_username:
            self._show_promote_admin_menu(user)
            return

        if selection_id == "yes":
            # Show broadcast choice menu
            self._show_broadcast_choice_menu(user, "promote", target_username)
        else:
            # No or back - return to promote admin menu
            self._show_promote_admin_menu(user)

    async def _handle_demote_confirm_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle demote confirmation menu selection."""
        target_username = state.get("target_username")
        if not target_username:
            self._show_demote_admin_menu(user)
            return

        if selection_id == "yes":
            # Show broadcast choice menu
            self._show_broadcast_choice_menu(user, "demote", target_username)
        else:
            # No or back - return to demote admin menu
            self._show_demote_admin_menu(user)

    async def _handle_kick_selection(
        self, user: NetworkUser, selection_id: str
    ) -> None:
        """Handle kick user menu selection."""
        if selection_id == "back":
            self._show_admin_menu(user)
        elif selection_id.startswith("kick_"):
            target_username = selection_id[5:]  # Remove "kick_" prefix
            self._show_kick_confirm_menu(user, target_username)

    async def _handle_kick_confirm_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle kick confirmation menu selection."""
        target_username = state.get("target_username")
        if not target_username:
            self._show_kick_menu(user)
            return

        if selection_id == "yes":
            await self._kick_user(user, target_username)
        else:
            # No or back - return to kick menu
            # Or return to admin menu directly? Usually back to list is better to verify safety.
            # But here "No" usually means "Cancel action".
            self._show_kick_menu(user)

    async def _handle_broadcast_choice_selection(
        self, user: NetworkUser, selection_id: str, state: dict
    ) -> None:
        """Handle broadcast choice menu selection."""
        action = state.get("action")
        target_username = state.get("target_username")

        if not action or not target_username:
            self._show_admin_menu(user)
            return

        # Determine broadcast scope: "all", "admins", or "nobody"
        broadcast_scope = selection_id  # "all", "admins", or "nobody"

        if action == "promote":
            await self._promote_to_admin(user, target_username, broadcast_scope)
        elif action == "demote":
            await self._demote_from_admin(user, target_username, broadcast_scope)

    # ==================== Admin Actions ====================

    @require_admin
    async def _approve_user(self, admin: NetworkUser, username: str) -> None:
        """Approve a pending user account."""
        if self._db.approve_user(username):
            admin.speak_l("account-approved", player=username)

            # Notify other admins of the account action
            self._notify_admins(
                "account-action", "accountactionnotify.ogg", exclude_username=admin.username
            )

            # Check if the user is online and waiting for approval
            waiting_user = self._users.get(username)
            if waiting_user:
                # Update the user's approved status so they can now interact
                waiting_user.set_approved(True)

                waiting_state = self._user_states.get(username, {})
                if waiting_state.get("menu") == "waiting_for_approval":
                    # User is online and waiting - welcome them and show main menu
                    waiting_user.speak_l("account-approved-welcome")
                    waiting_user.play_sound("accountapprove.ogg")
                    self._show_main_menu(waiting_user)

        self._show_account_approval_menu(admin)

    @require_admin
    async def _decline_user(self, admin: NetworkUser, username: str) -> None:
        """Decline and delete a pending user account."""
        # Check if the user is online first
        waiting_user = self._users.get(username)

        if self._db.delete_user(username):
            admin.speak_l("account-declined", player=username)

            # Notify other admins of the account action
            self._notify_admins(
                "account-action", "accountactionnotify.ogg", exclude_username=admin.username
            )

            # If user is online, disconnect them
            if waiting_user:
                waiting_user.speak_l("account-declined-goodbye")
                await waiting_user.connection.send({"type": "disconnect", "reconnect": False})

        self._show_account_approval_menu(admin)

    @require_admin
    async def _promote_to_admin(
        self, admin: NetworkUser, username: str, broadcast_scope: str
    ) -> None:
        """Promote a user to admin."""
        # Update trust level in database
        self._db.update_user_trust_level(username, 2)

        # Update the user's trust level if they are online
        target_user = self._users.get(username)
        if target_user:
            target_user.set_trust_level(2)

        # Always notify the target user with personalized message
        if target_user:
            target_user.speak_l("promote-announcement-you")
            target_user.play_sound("accountpromoteadmin.ogg")

        # Broadcast the announcement to others based on scope
        if broadcast_scope == "nobody":
            # Silent mode - only notify the admin who performed the action
            admin.speak_l("promote-announcement", player=username)
            admin.play_sound("accountpromoteadmin.ogg")
        else:
            # Broadcast to all or admins (excluding the target user who already got personalized message)
            self._broadcast_admin_change(
                "promote-announcement",
                "accountpromoteadmin.ogg",
                username,
                broadcast_scope,
                exclude_username=username,
            )

        self._show_admin_menu(admin)

    @require_admin
    async def _demote_from_admin(
        self, admin: NetworkUser, username: str, broadcast_scope: str
    ) -> None:
        """Demote an admin to regular user."""
        # Check target trust level first
        target_record = self._db.get_user(username)
        if not target_record:
            return
            
        if target_record.trust_level >= 3:
            # Cannot demote developer
            admin.speak_l("permission-denied") # Fallback or new key
            return

        # Update trust level in database
        self._db.update_user_trust_level(username, 1)

        # Update the user's trust level if they are online
        target_user = self._users.get(username)
        if target_user:
            target_user.set_trust_level(1)

        # Always notify the target user with personalized message
        if target_user:
            target_user.speak_l("demote-announcement-you")
            target_user.play_sound("accountdemoteadmin.ogg")

        # Broadcast the announcement to others based on scope
        if broadcast_scope == "nobody":
            # Silent mode - only notify the admin who performed the action
            admin.speak_l("demote-announcement", player=username)
            admin.play_sound("accountdemoteadmin.ogg")
        else:
            # Broadcast to all or admins (excluding the target user who already got personalized message)
            self._broadcast_admin_change(
                "demote-announcement",
                "accountdemoteadmin.ogg",
                username,
                broadcast_scope,
                exclude_username=username,
            )

        self._show_admin_menu(admin)

    def _broadcast_admin_change(
        self,
        message_id: str,
        sound: str,
        player_name: str,
        broadcast_scope: str,
        exclude_username: str | None = None,
    ) -> None:
        """Broadcast an admin promotion/demotion announcement."""
        for username, user in self._users.items():
            if not user.approved:
                continue  # Don't send broadcasts to unapproved users
            if exclude_username and username == exclude_username:
                continue  # Skip the excluded user
            if broadcast_scope == "admins" and user.trust_level < 2:
                continue  # Only admins if broadcasting to admins only
            user.speak_l(message_id, player=player_name)
            user.play_sound(sound)

    def _show_broadcast_input_menu(self, user: NetworkUser) -> None:
        """Show input box for broadcast message."""
        user.show_editbox(
            "broadcast_message",
            Localization.get(user.locale, "admin-broadcast-prompt"),
            multiline=True,
        )
        self._user_states[user.username] = {
            "menu": "admin_broadcast_input",
        }

    async def _handle_admin_input(
        self, user: NetworkUser, packet: dict, state: dict
    ) -> bool:
        """
        Handle input from an admin menu editbox.
        Returns True if handled, False otherwise.
        """
        menu_id = state.get("menu")
        input_id = packet.get("input_id")
        value = packet.get("text", packet.get("value")) # Support both just in case

        if menu_id == "admin_broadcast_input" and input_id == "broadcast_message":
            if value:
                await self._perform_broadcast(user, value)
            else:
                # Cancelled or empty
                self._show_admin_menu(user)
            return True

        return False

        admin.speak_l("admin-broadcast-sent", count=count)
        # self._show_admin_menu(admin) # Don't show menu immediately so they can hear report

    @require_admin
    async def _perform_broadcast(self, admin: NetworkUser, message: str) -> None:
        """Perform the broadcast action."""
        # Clean up message
        message = message.strip()
        if not message:
            self._show_admin_menu(admin)
            return

        # Prepare packets
        chat_packet = {
            "type": "chat",
            "convo": "announcement",
            "sender": admin.username, # Sender is still useful for logging/auditing but ignored by client display
            "message": message, # Raw message, client adds prefix
        }
        
        # Sound packet is no longer needed as client plays sound for "announcement" convo
        # But we previously added it to force sound. Since we updated client, we can remove it.
        # However, to support older clients (if any), we could keep it, but user said "Ensure System Announcement exists in en and vi".
        # This implies client update is expected. Let's remove the redundancy to be clean.
        
        count = 0
        total_online = len(self._users)
        
        # We iterate a copy of values to be safe against dictionary changes during async await
        users_list = list(self._users.values())
        
        for user in users_list:
            if user.approved:
                try:
                    # Send Chat
                    await user.connection.send(chat_packet)
                    count += 1
                except Exception as e:
                    print(f"Failed to broadcast to {user.username}: {e}")

        # Send confirmation to admin using speak_l (this uses queue, which is fine for local feedback)
        admin.speak_l("admin-broadcast-sent", count=count)
        
        # Also play a confirmation sound for admin locally via queue
        # admin.play_sound("notify.ogg") 
        
        self._show_admin_menu(admin)

    # ==================== Kick System ====================

    def _show_kick_menu(self, user: NetworkUser) -> None:
        """Show kick menu with list of online users."""
        # Get all online users except self and those with higher/equal immunity
        # Admin (2) cannot kick Admin (2) or Dev (3) ?
        # Rule: "Dev and admin can kick a user."
        # Rule: "Dev can promote/demote admin but admin cannot promote/demote dev".
        # Implied: Admin cannot kick Dev.
        # Can Admin kick Admin? Usually yes, or maybe not. 
        # "Dev and admin can kick a user." -> "A user" usually implies normal user.
        # But let's assume standard hierarchy: Admin can kick < 2. Dev can kick < 3.
        
        target_users = []
        for u in self._users.values():
            if u.username == user.username:
                continue
            
            # Immunity Check
            if u.trust_level >= 3:
                continue # Never show Devs
            
            if user.trust_level < 3 and u.trust_level >= 2:
                 continue # Admin cannot kick other Admins (Safety)
            
            target_users.append(u)

        if not target_users:
            user.speak_l("no-users-to-kick") # Reuse or add key if needed. Or just "no-actions-available"
            self._show_admin_menu(user)
            return

        items = []
        for target in target_users:
             items.append(MenuItem(text=target.username, id=f"kick_{target.username}"))
        items.append(MenuItem(text=Localization.get(user.locale, "back"), id="back"))

        user.show_menu(
            "kick_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {"menu": "kick_menu"}

    def _show_kick_confirm_menu(self, user: NetworkUser, target_username: str) -> None:
        """Show confirmation menu for kicking a user."""
        user.speak_l("kick-confirm", player=target_username)
        items = [
            MenuItem(text=Localization.get(user.locale, "confirm-yes"), id="yes"),
            MenuItem(text=Localization.get(user.locale, "confirm-no"), id="no"),
        ]
        user.show_menu(
            "kick_confirm_menu",
            items,
            multiletter=True,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )
        self._user_states[user.username] = {
            "menu": "kick_confirm_menu",
            "target_username": target_username,
        }

    @require_admin
    async def _kick_user(self, admin: NetworkUser, target_username: str) -> None:
        """Kick a user from the server."""
        # Check if user is online
        target_user = self._users.get(target_username)
        if not target_user:
            admin.speak_l("user-not-online", target=target_username)
            return

        # Check immunity
        if target_user.trust_level >= 3:
            admin.speak_l("permission-denied")
            return
        
        if admin.trust_level < 3 and target_user.trust_level >= 2:
             admin.speak_l("permission-denied")
             return

        # Logic
        # 1. Broadcast Global Message (Chat + Sound)
        # "kick-broadcast" = "{target} was kicked by {actor}."
        kick_msg = Localization.get(admin.locale, "kick-broadcast", target=target_username, actor=admin.username) # Use admin locale for raw log, or better: localize per client
        
        # We need a broadcast method that handles parameters. _broadcast_presence_l is close but fixed keys.
        # Let's manually iterate to localize properly.
        
        for u in self._users.values():
            if u.approved:
                u.speak_l("kick-broadcast", target=target_username, actor=admin.username)
                u.play_sound("kick.ogg")

        # 2. Notify Target
        # "you-were-kicked"
        target_user.speak_l("you-were-kicked", actor=admin.username)
        
        # 3. Force Exit Target
        await target_user.connection.send({"type": "force_exit", "reason": "kicked"})
        # Failsafe disconnect
        asyncio.create_task(self._kick_disconnect_delay(target_user))

        # 4. Return Admin to Menu
        self._show_admin_menu(admin)

    async def _kick_disconnect_delay(self, user):
         await asyncio.sleep(1.0)
         try:
             await user.connection.close(1000, "Kicked")
         except:
             pass
