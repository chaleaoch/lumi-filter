"""
Test util module functionality

This file tests:
- ClassHierarchyMapping class
- Method resolution order lookups
- Mapping interface implementation
"""

import pytest

from lumi_filter.util import ClassHierarchyMapping


class TestClassHierarchyMapping:
    """Test ClassHierarchyMapping class"""

    def test_init_empty(self):
        """Test initialization with no mapping"""
        mapping = ClassHierarchyMapping()
        assert len(mapping) == 0
        assert not mapping.data

    def test_init_with_mapping(self):
        """Test initialization with initial mapping"""
        initial = {str: "string", int: "integer"}
        mapping = ClassHierarchyMapping(initial)
        assert len(mapping) == 2
        assert mapping[str] == "string"
        assert mapping[int] == "integer"

    def test_setitem_getitem(self):
        """Test setting and getting items"""
        mapping = ClassHierarchyMapping()
        mapping[str] = "string_field"
        mapping[int] = "int_field"

        assert mapping[str] == "string_field"
        assert mapping[int] == "int_field"

    def test_delitem(self):
        """Test deleting items"""
        mapping = ClassHierarchyMapping({str: "string"})
        del mapping[str]

        with pytest.raises(KeyError):
            mapping[str]

    def test_iter(self):
        """Test iteration over mapping"""
        initial = {str: "string", int: "integer"}
        mapping = ClassHierarchyMapping(initial)

        keys = list(mapping)
        assert str in keys
        assert int in keys
        assert len(keys) == 2

    def test_len(self):
        """Test length of mapping"""
        mapping = ClassHierarchyMapping()
        assert len(mapping) == 0

        mapping[str] = "string"
        assert len(mapping) == 1

        mapping[int] = "integer"
        assert len(mapping) == 2

    def test_contains_direct_match(self):
        """Test contains with direct type match"""
        mapping = ClassHierarchyMapping({str: "string"})
        assert str in mapping
        assert int not in mapping

    def test_contains_inheritance_match(self):
        """Test contains with inheritance hierarchy"""

        class Parent:
            pass

        class Child(Parent):
            pass

        mapping = ClassHierarchyMapping({Parent: "parent_field"})

        # Child should be found via MRO
        assert Parent in mapping
        assert Child in mapping

    def test_getitem_inheritance_lookup(self):
        """Test getting item via inheritance hierarchy"""

        class Parent:
            pass

        class Child(Parent):
            pass

        class GrandChild(Child):
            pass

        mapping = ClassHierarchyMapping({Parent: "parent_field"})

        # All should resolve to parent_field via MRO
        assert mapping[Parent] == "parent_field"
        assert mapping[Child] == "parent_field"
        assert mapping[GrandChild] == "parent_field"

    def test_getitem_most_specific_match(self):
        """Test getting most specific match in hierarchy"""

        class Parent:
            pass

        class Child(Parent):
            pass

        mapping = ClassHierarchyMapping({Parent: "parent_field", Child: "child_field"})

        # Parent should get parent_field
        assert mapping[Parent] == "parent_field"
        # Child should get child_field (more specific)
        assert mapping[Child] == "child_field"

    def test_getitem_key_error(self):
        """Test KeyError for unmapped type"""

        class Unmapped:
            pass

        mapping = ClassHierarchyMapping({str: "string"})

        with pytest.raises(KeyError):
            mapping[Unmapped]

    def test_mutable_mapping_interface(self):
        """Test that it properly implements MutableMapping"""
        from collections.abc import MutableMapping

        mapping = ClassHierarchyMapping()
        assert isinstance(mapping, MutableMapping)

    def test_builtin_types_hierarchy(self):
        """Test with built-in type hierarchy"""
        # bool is a subclass of int in Python
        mapping = ClassHierarchyMapping({int: "integer_field"})

        assert mapping[int] == "integer_field"
        assert mapping[bool] == "integer_field"  # bool should find int via MRO

    def test_complex_hierarchy(self):
        """Test complex inheritance hierarchy"""

        class A:
            pass

        class B(A):
            pass

        class C(A):
            pass

        class D(B, C):
            pass

        mapping = ClassHierarchyMapping({A: "a_field", B: "b_field"})

        assert mapping[A] == "a_field"
        assert mapping[B] == "b_field"
        assert mapping[C] == "a_field"  # C inherits from A
        assert (
            mapping[D] == "b_field"
        )  # D inherits from B (first in MRO after D itself)
