"""Tests for util module."""

from typing import Union

import pytest

from lumi_filter.util import ClassHierarchyMapping


class TestClassHierarchyMapping:
    """Test the ClassHierarchyMapping class."""

    def test_init_empty(self):
        """Test initialization with no mapping."""
        mapping = ClassHierarchyMapping()
        assert len(mapping) == 0
        assert mapping.data == {}

    def test_init_with_mapping(self):
        """Test initialization with initial mapping."""
        initial = {str: "string_handler", int: "int_handler"}
        mapping = ClassHierarchyMapping(initial)
        assert len(mapping) == 2
        assert mapping.data == initial

    def test_setitem_and_getitem(self):
        """Test setting and getting items."""
        mapping = ClassHierarchyMapping()
        mapping[str] = "string_handler"
        mapping[int] = "int_handler"

        assert mapping[str] == "string_handler"
        assert mapping[int] == "int_handler"

    def test_delitem(self):
        """Test deleting items."""
        mapping = ClassHierarchyMapping({str: "string_handler", int: "int_handler"})
        del mapping[str]

        assert len(mapping) == 1
        assert str not in mapping.data
        assert int in mapping.data

    def test_iter(self):
        """Test iteration over mapping."""
        initial = {str: "string_handler", int: "int_handler"}
        mapping = ClassHierarchyMapping(initial)

        keys = list(mapping)
        assert set(keys) == {str, int}

    def test_len(self):
        """Test length calculation."""
        mapping = ClassHierarchyMapping()
        assert len(mapping) == 0

        mapping[str] = "handler"
        assert len(mapping) == 1

        mapping[int] = "handler"
        assert len(mapping) == 2

    def test_inheritance_lookup(self):
        """Test that inheritance hierarchy is respected in lookups."""

        class BaseClass:
            pass

        class DerivedClass(BaseClass):
            pass

        class GrandchildClass(DerivedClass):
            pass

        mapping = ClassHierarchyMapping()
        mapping[BaseClass] = "base_handler"

        # Direct lookup should work
        assert mapping[BaseClass] == "base_handler"

        # Derived classes should find parent handler
        assert mapping[DerivedClass] == "base_handler"
        assert mapping[GrandchildClass] == "base_handler"

    def test_inheritance_override(self):
        """Test that more specific class mappings override general ones."""

        class BaseClass:
            pass

        class DerivedClass(BaseClass):
            pass

        mapping = ClassHierarchyMapping()
        mapping[BaseClass] = "base_handler"
        mapping[DerivedClass] = "derived_handler"

        # Base class should get base handler
        assert mapping[BaseClass] == "base_handler"

        # Derived class should get its specific handler
        assert mapping[DerivedClass] == "derived_handler"

    def test_mro_order(self):
        """Test that Method Resolution Order is followed correctly."""

        class A:
            pass

        class B:
            pass

        class C(A, B):
            pass

        mapping = ClassHierarchyMapping()
        mapping[A] = "a_handler"
        mapping[B] = "b_handler"

        # C should find A's handler first (due to MRO)
        assert mapping[C] == "a_handler"

    def test_union_type_lookup(self):
        """Test lookup with Union types."""
        mapping = ClassHierarchyMapping()
        mapping[str] = "string_handler"
        mapping[int] = "int_handler"

        # Create a Union type
        try:
            union_type = Union[str, int]

            # Should find the first matching type in the union
            result = mapping[union_type]
            assert result in ["string_handler", "int_handler"]
        except (AttributeError, TypeError):
            # Skip this test if Union types don't work properly in this environment
            pytest.skip("Union type handling not available in this environment")

    def test_modern_union_syntax(self):
        """Test lookup with modern union syntax (str | int)."""
        mapping = ClassHierarchyMapping()
        mapping[str] = "string_handler"
        mapping[int] = "int_handler"

        # Create a union type using | syntax (Python 3.10+)
        union_type = str | int

        # Should find one of the handlers
        result = mapping[union_type]
        assert result in ["string_handler", "int_handler"]

    def test_key_not_found(self):
        """Test KeyError when key is not found."""
        mapping = ClassHierarchyMapping()
        mapping[str] = "string_handler"

        with pytest.raises(KeyError):
            _ = mapping[int]

    def test_key_not_found_with_inheritance(self):
        """Test KeyError when no parent class is found either."""

        class UnmappedClass:
            pass

        mapping = ClassHierarchyMapping()
        mapping[str] = "string_handler"

        with pytest.raises(KeyError):
            _ = mapping[UnmappedClass]

    def test_builtin_type_inheritance(self):
        """Test inheritance with built-in types."""
        mapping = ClassHierarchyMapping()
        mapping[object] = "object_handler"

        # All classes inherit from object
        assert mapping[str] == "object_handler"
        assert mapping[int] == "object_handler"
        assert mapping[list] == "object_handler"

    def test_complex_inheritance_hierarchy(self):
        """Test complex inheritance scenarios."""

        class Animal:
            pass

        class Mammal(Animal):
            pass

        class Dog(Mammal):
            pass

        class Labrador(Dog):
            pass

        mapping = ClassHierarchyMapping()
        mapping[Animal] = "animal_handler"
        mapping[Mammal] = "mammal_handler"

        # Test that most specific mapping is found
        assert mapping[Animal] == "animal_handler"
        assert mapping[Mammal] == "mammal_handler"
        assert mapping[Dog] == "mammal_handler"  # Inherits from Mammal
        assert mapping[Labrador] == "mammal_handler"  # Inherits from Mammal

    def test_multiple_inheritance_diamond(self):
        """Test diamond inheritance pattern."""

        class Base:
            pass

        class Left(Base):
            pass

        class Right(Base):
            pass

        class Diamond(Left, Right):
            pass

        mapping = ClassHierarchyMapping()
        mapping[Base] = "base_handler"
        mapping[Left] = "left_handler"

        # Diamond should find Left first due to MRO
        assert mapping[Diamond] == "left_handler"

    def test_mapping_mutation(self):
        """Test that mapping can be modified after creation."""
        mapping = ClassHierarchyMapping({str: "original"})

        # Modify existing mapping
        mapping[str] = "modified"
        assert mapping[str] == "modified"

        # Add new mapping
        mapping[int] = "new"
        assert mapping[int] == "new"

        # Delete mapping
        del mapping[str]
        with pytest.raises(KeyError):
            _ = mapping[str]

    def test_empty_mapping_operations(self):
        """Test operations on empty mapping."""
        mapping = ClassHierarchyMapping()

        assert len(mapping) == 0
        assert list(mapping) == []

        with pytest.raises(KeyError):
            _ = mapping[str]
