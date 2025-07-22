"""lumi_filter: A powerful and flexible data filtering library.

lumi_filter provides a unified interface for filtering and ordering data
across different sources including Peewee ORM queries, Pydantic models,
and iterable data structures.

Key Features:
- Universal filtering interface for multiple data sources
- Automatic field type detection and mapping
- Support for complex lookup expressions
- Seamless integration with Peewee ORM and Pydantic models
- Extensible field types and operators
"""

from .field import IntField, StrField  # noqa: F401
from .model import Model  # noqa: F401
