"""Backend package initialisation.

This file marks the backend directory as a Python package and can be used
to expose top‑level modules or shared objects.  Currently it simply
imports the settings object for convenience.
"""

from .config import settings  # noqa: F401

__all__ = ["settings"]