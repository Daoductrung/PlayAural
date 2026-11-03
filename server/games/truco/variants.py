"""Rule sets for the Truco variants.

``TrucoGame`` picks one of these per table from its ``variant`` option. Each
class is a plain mixin: its attributes and methods override the engine's
Argentine defaults when that variant is selected, and run with ``self`` bound
to the game.
"""

from __future__ import annotations

from typing import ClassVar

from ...messages.localization import Localization
from ...ui.keybinds import KeybindState
from ..base import Player
from . import audio, decks, rules
from .cards import TrucoCard
from .engine import TrucoPlayer

VARIANT_ARGENTINE = "argentine"
VARIANT_BRAZILIAN = "brazilian"
VARIANT_SPANISH = "spanish"
VARIANT_CHOICES = [VARIANT_ARGENTINE, VARIANT_BRAZILIAN, VARIANT_SPANISH]
BRAZILIAN_TARGET = 12


class ArgentineRules:
    """Argentine Truco: Spanish 40-card deck, envido, optional flor, mazo."""

    def _flor_enabled(self) -> bool:
        return bool(self.options.flor)

    def _bot_strength(self, card: TrucoCard) -> float:
        return card.power


class BrazilianRules:
    """Truco Paulista: French deck, vira and manilhas, 3/6/9/12, mão de onze."""

    LADDER = ("truco", "seis", "nove", "doze")
    LEVEL_POINTS: ClassVar[dict] = {"truco": 3, "seis": 6, "nove": 9, "doze": 12}
    LEVEL_DECLINED: ClassVar[dict] = {"truco": 1, "seis": 3, "nove": 6, "doze": 9}
    CALL_KEYS: ClassVar[dict] = {
        "truco": "trucobrazilian-call-truco",
        "seis": "trucobrazilian-call-seis",
        "nove": "trucobrazilian-call-nove",
        "doze": "trucobrazilian-call-doze",
        "onze": "trucobrazilian-call-onze",
    }
    CALL_ACTIONS: ClassVar[dict] = {"call_truco": "truco"}
    CALL_ACTION_ORDER: ClassVar[list] = ["call_truco"]
    MSG: ClassVar[dict] = {
        "truco-game-start-no-flor": "trucobrazilian-game-start",
        "truco-action-accept": "trucobrazilian-action-accept",
        "truco-action-decline": "trucobrazilian-action-decline",
        "truco-accept-you": "trucobrazilian-accept-you",
        "truco-accept-player": "trucobrazilian-accept-player",
        "truco-decline-you": "trucobrazilian-decline-you",
        "truco-decline-player": "trucobrazilian-decline-player",
        "truco-pending-answer": "trucobrazilian-pending-answer",
        "truco-error-answer-first": "trucobrazilian-error-answer-first",
        "truco-error-raise-max": "trucobrazilian-error-raise-max",
        "truco-trick-tie": "truco-trick-tie-neutral",
    }
    ENVIDO_ENABLED = False
    HAS_MAZO = False
    USES_VIRA = True
    MAO_DE_ONZE = True
    MUSIC = audio.MUSIC_BRAZILIAN

    def _target_value(self) -> int:
        return BRAZILIAN_TARGET

    def _build_deck(self) -> list[TrucoCard]:
        return decks.build_french_deck()

    def _power(self, card: TrucoCard) -> int:
        return decks.brazilian_power(card, self.vira)

    def _sort_card(self, card: TrucoCard) -> tuple:
        return (self._power(card), decks.FRENCH_SUITS.index(card.suit))

    def _format_card(self, card: TrucoCard, locale: str) -> str:
        return decks.format_french_card(card, locale)

    def _decide_hand(self, mano_team: int) -> int | None:
        return rules.decide_hand_annulling(self.trick_results)

    def _bot_strength(self, card: TrucoCard) -> float:
        # Manilhas sit at the top of the scale; ordinary cards spread below it.
        power = self._power(card)
        if power >= decks.MANILHA_BASE:
            return 11 + (power - decks.MANILHA_BASE)
        return power * 1.0

    def _manilha_text(self, locale: str) -> str:
        if self.vira is None:
            return ""
        rank = decks.manilha_rank(self.vira)
        key = decks.FRENCH_RANK_KEYS.get(rank)
        return Localization.get(locale, key) if key else str(rank)

    def _announce_vira(self) -> None:
        vira = self.vira
        if vira is None:
            return
        self.play_sound(audio.VIRA_REVEAL)
        for listener in self.players:
            user = self.get_user(listener)
            if user:
                user.speak_l(
                    "trucobrazilian-vira",
                    buffer="game",
                    card=self._format_card(vira, user.locale),
                    manilha=self._manilha_text(user.locale),
                )

    def _extra_info_actions(self) -> list[tuple[str, str, str, bool]]:
        return [("read_vira", "trucobrazilian-read-vira", "_action_read_vira", False)]

    def _extra_keybinds(self) -> None:
        self.define_keybind(
            "v",
            "Read the vira and manilha",
            ["read_vira"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    def _action_read_vira(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        if self.vira is None:
            user.speak_l("trucobrazilian-no-vira", buffer="game")
            return
        user.speak_l(
            "trucobrazilian-vira-is",
            buffer="game",
            card=self._format_card(self.vira, user.locale),
            manilha=self._manilha_text(user.locale),
        )

    def _blind_hand(self) -> bool:
        scores = self._scores()
        return len(scores) == 2 and all(score == self.target - 1 for score in scores)

    def _start_onze(self) -> bool:
        scores = self._scores()
        at_eleven = [i for i, score in enumerate(scores) if score == self.target - 1]
        if len(at_eleven) == 2:
            self.no_calls = True
            self.play_sound(audio.MAO_DE_ONZE)
            self.broadcast_l("trucobrazilian-ferro", buffer="game")
            return False
        if len(at_eleven) != 1:
            return False
        team = at_eleven[0]
        self.onze_team = team
        self.onze_pending = True
        self.play_sound(audio.MAO_DE_ONZE)
        mine_ids = {p.id for p in self._team_players(team, live_only=True)}
        for listener in self.players:
            user = self.get_user(listener)
            if not user:
                continue
            if listener.id in mine_ids:
                user.speak_l("trucobrazilian-onze-your-team", buffer="game")
                if isinstance(listener, TrucoPlayer):
                    self._speak_partner_cards(listener, user)
            else:
                user.speak_l(
                    "trucobrazilian-onze-team",
                    buffer="game",
                    **self._resolve_broadcast_kwargs(
                        user.locale, {"team": self._team_label(team)}
                    ),
                )
        self._jolt()
        self.refresh_menus()
        return True


class SpanishRules:
    """Spanish Truc (Valencian): 22-card deck, envit/torna/la falta, joc fora.

    Reference rules: the game is won with two cames. The 24-point came (default)
    comes from the Campionat Faller de Truc of València, the ETSIADI-UPV
    tournament and the Truc regulation on fallas.com; the 18-point came is the
    Falles de Torrent bases and the Museu d'Història de València description.
    Joc fora wins the whole game as in the UPV bases (the Torrent bases limit it to the coto), and la falta is
    what the leader still needs to finish the current came (both bases). The
    envit values (envit 2, torna 4 in total, la falta = what the leader needs;
    a refused first call pays 1 and a refused raise pays the value already
    accepted: 2 after an envit, 4 after a torna) follow the Reglamento del Truc of
    the Falles and the Truc Valencià Online guide. The Torrent and UPV bases play
    without envit. When all three tricks tie, the player nearest the mano among
    those who tied the last trick wins (Falles and Salvagim).
    """

    PLAYER_MODES: ClassVar[dict] = {2: "individual", 4: "2v2"}
    LADDER = ("truco", "retruco", "valecuatro", "jocfora")
    LEVEL_POINTS: ClassVar[dict] = {
        "truco": 2,
        "retruco": 3,
        "valecuatro": 4,
        "jocfora": -1,
    }
    LEVEL_DECLINED: ClassVar[dict] = {
        "truco": 1,
        "retruco": 2,
        "valecuatro": 3,
        "jocfora": 4,
    }
    CALL_KEYS: ClassVar[dict] = {
        "truco": "trucospanish-call-truc",
        "retruco": "trucospanish-call-retruc",
        "valecuatro": "trucospanish-call-quatre-val",
        "jocfora": "trucospanish-call-joc-fora",
        rules.ENVIDO: "trucospanish-call-envit",
        rules.REAL_ENVIDO: "trucospanish-call-torna",
        rules.FALTA_ENVIDO: "trucospanish-call-la-falta",
    }
    CALL_ACTIONS: ClassVar[dict] = {
        "call_truco": "truco",
        "call_envido": rules.ENVIDO,
        "call_real_envido": rules.REAL_ENVIDO,
        "call_falta_envido": rules.FALTA_ENVIDO,
    }
    CALL_ACTION_ORDER: ClassVar[list] = [
        "call_envido",
        "call_real_envido",
        "call_falta_envido",
        "call_truco",
    ]
    MSG: ClassVar[dict] = {
        "truco-action-accept": "trucospanish-action-accept",
        "truco-action-decline": "trucospanish-action-decline",
        "truco-action-mazo": "trucospanish-action-mazo",
        "truco-accept-you": "trucospanish-accept-you",
        "truco-accept-player": "trucospanish-accept-player",
        "truco-decline-you": "trucospanish-decline-you",
        "truco-decline-player": "trucospanish-decline-player",
        "truco-mazo-you": "trucospanish-mazo-you",
        "truco-mazo-player": "trucospanish-mazo-player",
        "truco-reason-truco": "trucospanish-reason-truc",
        "truco-reason-envido": "trucospanish-reason-envit",
        "truco-game-start-no-flor": "trucospanish-game-start",
        "truco-desc-mazo": "trucospanish-desc-mazo",
        "truco-pending-answer": "trucospanish-pending-answer",
        "truco-error-answer-first": "trucospanish-error-answer-first",
        "truco-error-raise-max": "trucospanish-error-raise-max",
        "truco-error-bad-count": "trucospanish-error-bad-count",
        "truco-error-team-mode-count": "trucospanish-error-team-mode-count",
        "truco-status-envido-open": "trucospanish-status-envit-open",
        "truco-status-envido-closed": "trucospanish-status-envit-closed",
        "truco-status-no-truco": "trucospanish-status-no-truc",
        "truco-falta-envido-value": "trucospanish-falta-value",
        "truco-reveal-envido-you": "trucospanish-reveal-envit-you",
        "truco-reveal-envido-player": "trucospanish-reveal-envit-player",
        "truco-error-envido-late": "trucospanish-error-envit-late",
        "truco-error-envido-closed": "trucospanish-error-envit-closed",
        "truco-error-envido-done": "trucospanish-error-envit-done",
        "truco-error-envido-cannot-raise": "trucospanish-error-envit-cannot-raise",
        "truco-trick-tie": "truco-trick-tie-neutral",
        "truco-score-line": "trucospanish-score-line",
        "truco-game-win-you": "trucospanish-game-win-you",
        "truco-game-win-player": "trucospanish-game-win-player",
        "truco-game-win-your-team": "trucospanish-game-win-your-team",
        "truco-game-win-team": "trucospanish-game-win-team",
        "truco-end-line": "trucospanish-end-line",
    }
    FOLD_SCOPE = "team"
    MUSIC = audio.MUSIC_SPANISH
    CAMES_TO_WIN = 2

    def _target_value(self) -> int:
        return int(self.options.spanish_length)

    def _build_deck(self) -> list[TrucoCard]:
        return decks.build_spanish_deck()

    def _power(self, card: TrucoCard) -> int:
        return decks.spanish_power(card)

    def _sort_card(self, card: TrucoCard) -> tuple:
        return (self._power(card), card.id)

    def _tie_break_team(self, top_plays: list, mano_team: int) -> int:
        """All three tricks tied: the player nearest the mano among those who tied the last one wins."""

        position = {
            player.id: index
            for index, player in enumerate(self._order_from(self.mano_index))
        }
        first = min(top_plays, key=lambda play: position.get(play.player_id, 99))
        owner = self.get_player_by_id(first.player_id)
        return self._team_index(owner) if owner else mano_team

    def _can_add_envido(self, chain: list[str], call: str) -> bool:
        return rules.can_add_envit_call(chain, call)

    def _envido_accepted_points(self, chain: list[str], falta: int) -> int:
        return rules.envit_accepted_points(chain, falta)

    def _envido_declined_points(self, chain: list[str]) -> int:
        return rules.envit_declined_points(chain)

    def _falta_decides_game(self) -> bool:
        return False

    def _falta_points(self, winner_score: int = 0) -> int:
        return rules.envit_falta_points(self._scores(), self.target)

    def _on_points_awarded(self, team_index: int, old: int, new: int) -> None:
        # Cames are announced when one is won (see _close_came), not at a half-way mark.
        return None

    def _final_score(self, team) -> int:
        return self._cames(team.index)


RULE_SETS = {
    VARIANT_ARGENTINE: ArgentineRules,
    VARIANT_BRAZILIAN: BrazilianRules,
    VARIANT_SPANISH: SpanishRules,
}
