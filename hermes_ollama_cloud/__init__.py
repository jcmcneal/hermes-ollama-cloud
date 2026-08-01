"""Ollama Cloud web search + extract plugin for Hermes Agent.

Standalone plugin package. Install via ``pip install hermes-ollama-cloud``
or drop into ``~/.hermes/plugins/web/ollama/``.
"""

from __future__ import annotations

from .provider import OllamaWebSearchProvider


def register(ctx) -> None:
    """Register the Ollama Cloud provider with the plugin context."""
    ctx.register_web_search_provider(OllamaWebSearchProvider())
