import inspect
from collections import UserDict


class ClassHierarchyMapping(UserDict):
    def __init__(self, mapping):
        self.mapping = mapping

    def __getitem__(self, key):
        for cls in inspect.getmro(key):
            if cls in self.mapping:
                return self.mapping[cls]
        raise KeyError(f"No mapping found for class: {key}, mapping: {self.mapping}.")

    def __setitem__(self, key, value):
        self.mapping[key] = value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
