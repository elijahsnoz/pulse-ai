"""Tape persistence adapters (in-memory + JSON file)."""
from .tape_store import InMemoryTapeStore, JsonFileTapeStore

__all__ = ["InMemoryTapeStore", "JsonFileTapeStore"]
