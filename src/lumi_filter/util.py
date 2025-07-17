import inspect
from collections import UserDict
from typing import Any, Dict, Iterator, Type


class ClassHierarchyMapping(UserDict[Type, Any]):
    """
    A mapping that looks up values based on class hierarchy.

    When getting a value for a class, it searches through the Method Resolution Order (MRO)
    to find the most specific match. This is useful for mapping base classes to implementations
    that should also apply to their subclasses.

    Example:
        >>> mapping = ClassHierarchyMapping({str: "string_handler", object: "default_handler"})
        >>> mapping[str]  # Returns "string_handler"
        >>> mapping[int]  # Returns "default_handler" (int inherits from object)
    """

    def __init__(self, mapping: Dict[Type, Any], dict=None, /, **kwargs) -> None:
        """
        Initialize the ClassHierarchyMapping.

        Args:
            mapping: Dictionary mapping class types to values
            dict: Ignored parameter for UserDict compatibility
            **kwargs: Additional keyword arguments passed to UserDict
        """
        super().__init__(dict=None, **kwargs)
        self.data = mapping.copy()  # Use UserDict's data attribute

    def __getitem__(self, key: Type) -> Any:
        """
        Get value for a class, searching through its MRO.

        Args:
            key: The class type to look up

        Returns:
            The value associated with the class or its nearest parent class

        Raises:
            TypeError: If key is not a class
            KeyError: If no mapping found for the class or its parents
        """
        if not inspect.isclass(key):
            raise TypeError(f"Key must be a class, got {type(key)}")

        for cls in inspect.getmro(key):
            if cls in self.data:
                return self.data[cls]

        raise KeyError(f"No mapping found for class: {key.__name__}")

    def __setitem__(self, key: Type, value: Any) -> None:
        """
        Set value for a class.

        Args:
            key: The class type to map
            value: The value to associate with the class

        Raises:
            TypeError: If key is not a class
        """
        if not inspect.isclass(key):
            raise TypeError(f"Key must be a class, got {type(key)}")
        self.data[key] = value

    def get(self, key: Type, default: Any = None) -> Any:
        """
        Get value for a class with default fallback.

        Args:
            key: The class type to look up
            default: Value to return if no mapping found

        Returns:
            The mapped value or the default value
        """
        try:
            return self[key]
        except (KeyError, TypeError):
            return default

    def __contains__(self, key: Type) -> bool:
        """
        Check if any class in the MRO has a mapping.

        Args:
            key: The class type to check

        Returns:
            True if a mapping exists for the class or its parents
        """
        if not inspect.isclass(key):
            return False

        return any(cls in self.data for cls in inspect.getmro(key))

    def keys(self) -> Iterator[Type]:
        """Return an iterator over the mapped class types."""
        return iter(self.data.keys())

    def values(self) -> Iterator[Any]:
        """Return an iterator over the mapped values."""
        return iter(self.data.values())

    def items(self) -> Iterator[tuple[Type, Any]]:
        """Return an iterator over (class, value) pairs."""
        return iter(self.data.items())
