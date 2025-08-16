"""Utility classes for enhanced mapping functionality.

This module provides utility classes that extend standard mapping behavior
to support advanced lookup patterns and inheritance-based resolution.
"""

import inspect
import types
from collections.abc import MutableMapping
from typing import get_args


class ClassHierarchyMapping(MutableMapping):
    """Mapping that supports class hierarchy lookups via Method Resolution Order.

    This mapping class enables lookups that traverse the class hierarchy using
    Python's Method Resolution Order (MRO), allowing for inheritance-based
    field type resolution.

    :param mapping: Initial mapping data
    :type mapping: dict or None
    """

    def __init__(self, mapping=None):
        self.data = dict(mapping) if mapping else {}

    def __getitem__(self, key):
        if isinstance(key, types.UnionType):
            keys = get_args(key)
        else:
            keys = [key]
        for key in keys:
            for cls in inspect.getmro(key):
                if cls in self.data:
                    return self.data[cls]

        raise KeyError(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __contains__(self, key):
        return any(cls in self.data for cls in inspect.getmro(key))
