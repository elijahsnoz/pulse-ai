"""Entities: identity-bearing domain objects (compared by id, not value).

PROVISIONAL — NOT part of the frozen Module 1 v1.0 public contract.

``Team``, ``Match`` and ``MatchStatus`` are unused by the metric engine and are
expected to evolve in Module 2 (ingestion/persistence), where their real
consumers — TxLINE id mapping, repositories and status transitions — will shape
them. Treat their current shape as a placeholder, not a stable API.
"""
