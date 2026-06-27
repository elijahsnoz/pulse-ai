"""Presentation layer — FastAPI + WebSocket surface and the demo visualizer.

The thin outer edge: serializes ``MatchSnapshot``s and ``TimelineEvent``s for the
wire and streams them to the browser. No business logic lives here.
"""
