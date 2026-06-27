"""Infrastructure layer — concrete adapters implementing the application ports.

Tape persistence, the live TxLINE provider, the replay provider, and the
recording tee. Depends inward on ``application`` and ``domain``; nothing depends
on it.
"""
