import inspect
from collections.abc import MutableMapping


class ClassHierarchyMapping(MutableMapping):
    """Mapping that supports class hierarchy lookups via Method Resolution Order."""

    def __init__(self, mapping=None):
        self.data = dict(mapping) if mapping else {}

    def __getitem__(self, key):
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
