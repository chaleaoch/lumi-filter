"""
Shortcut module for convenient filter model creation.

This module provides utilities for quickly creating filter models
without explicit class definitions, useful for rapid prototyping
and dynamic filtering scenarios.
"""

from .shortcut import AutoQueryModel, compatible_request_args  # noqa: F401

__all__ = [
    "AutoQueryModel",
    "compatible_request_args",
]
