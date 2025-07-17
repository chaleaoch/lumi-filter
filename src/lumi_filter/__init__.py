"""
Lumi Filter - A flexible filtering system for Python data structures and ORM queries.

This package provides a unified interface for filtering and ordering data
from various sources including ORM queries (Peewee) and Python data structures
(lists, dictionaries). It supports type-safe field definitions, multiple
lookup expressions, and automatic field generation from model schemas.

Basic Usage:
    >>> from lumi_filter import Model, IntField, StrField
    >>>
    >>> class UserFilter(Model):
    ...     name = StrField()
    ...     age = IntField()
    >>>
    >>> users = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
    >>> filtered = UserFilter(users, {"age__gte": 25}).filter().result()

Advanced Usage with ORM:
    >>> class UserFilter(Model):
    ...     class Meta:
    ...         schema = User  # Peewee model
    >>>
    >>> query = User.select()
    >>> filtered = UserFilter(query, {"age__gte": 18}).filter().result()
"""

from .backend import IterableBackend, PeeweeBackend  # noqa: F401
from .field import (
    BooleanField,
    DateField,
    DateTimeField,
    DecimalField,
    FilterField,
    IntField,
    StrField,
)  # noqa: F401
from .model import MetaModel, Model  # noqa: F401
from .operator import (
    generic_ilike_operator,
    generic_is_null_operator,
    generic_like_operator,
)  # noqa: F401

# Shortcut imports for convenience
from .shortcut import AutoQueryModel, compatible_request_args  # noqa: F401
from .shortcut.dynamic_model import (  # noqa: F401
    create_dynamic_model,
    model_from_dict_schema,
)
from .util import ClassHierarchyMapping  # noqa: F401

__version__ = "0.1.0"
__author__ = "Lumi Filter Contributors"
__description__ = (
    "A flexible filtering system for Python data structures and ORM queries"
)

__all__ = [
    # Core classes
    "Model",
    "MetaModel",
    # Field types
    "FilterField",
    "IntField",
    "StrField",
    "DecimalField",
    "BooleanField",
    "DateField",
    "DateTimeField",
    # Backends
    "PeeweeBackend",
    "IterableBackend",
    # Utilities
    "ClassHierarchyMapping",
    # Operators
    "generic_like_operator",
    "generic_ilike_operator",
    "generic_is_null_operator",
    # Shortcuts
    "AutoQueryModel",
    "compatible_request_args",
    "create_dynamic_model",
    "model_from_dict_schema",
]
