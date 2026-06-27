"""Team — an identity-bearing competitor entity.

PROVISIONAL — not part of the frozen Module 1 v1.0 contract (see entities/__init__.py).

Purpose
    Represent a club/national side with stable identity. Entities are compared by
    identity (``id``), not by attribute value (contrast with value objects).

Invariants
    * ``id`` is the stable identity; equality and hashing derive from it alone.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(eq=False)
class Team:
    """A competing team identified by a stable ``id``."""

    id: str
    name: str
    short_name: str = ""
    country: str = ""
    crest_url: str | None = None

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Team) and other.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)
