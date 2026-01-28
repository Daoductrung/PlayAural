"""Shared action log helpers for poker games."""

from __future__ import annotations


def log_fold(log: list[tuple[str, dict]], player: str) -> None:
    log.append(("poker-log-fold", {"player": player}))


def log_check(log: list[tuple[str, dict]], player: str) -> None:
    log.append(("poker-log-check", {"player": player}))


def log_call(log: list[tuple[str, dict]], player: str, amount: int) -> None:
    log.append(("poker-log-call", {"player": player, "amount": amount}))


def log_raise(log: list[tuple[str, dict]], player: str, amount: int) -> None:
    log.append(("poker-log-raise", {"player": player, "amount": amount}))


def log_all_in(log: list[tuple[str, dict]], player: str, amount: int) -> None:
    log.append(("poker-log-all-in", {"player": player, "amount": amount}))
