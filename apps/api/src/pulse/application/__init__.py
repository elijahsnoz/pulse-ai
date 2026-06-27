"""Application layer (Module 2+).

Orchestration that sits ABOVE the frozen Module 1 ``domain`` and BELOW the
infrastructure adapters. Home of the ingestion/replay pipeline: canonical frames,
serialization, fingerprinting, the reducer, ports and use cases.

Depends on ``pulse.domain`` (v1.0); never the reverse.
"""
