"""Facade for LLM client - uses backend's provider-agnostic module."""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.src.llm.factory import get_llm_client as _get

# Re-export
get_llm_client = _get
