"""Frame source adapters: replay, recording tee, and live TxLINE."""
from .recorded import RecordedProvider
from .recorder import Recorder
from .txline import TxLineProvider, normalize_txline_event

__all__ = ["RecordedProvider", "Recorder", "TxLineProvider", "normalize_txline_event"]
