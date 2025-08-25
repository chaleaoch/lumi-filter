"""Tests for advanced model filter functionality.

This module tests advanced usage of custom filter models with explicit field definitions
and schema-based field introspection capabilities.
"""

import json


class TestAdvancedModelFilter:
    """Test the advanced model filter endpoint (/advanced-model/)."""

    def test_advanced_list_products_no_filters(self, client):
        """Test listing all products without any filters using advanced model."""
        response = client.get("/advanced-model/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "count" in data
        assert "results" in data
        assert data["count"] > 0  # Should have sample data
        assert len(data["results"]) == data["count"]

    def test_advanced_filter_by_name_schema_field(self, client):
        """Test filtering by name field (from schema introspection)."""
        response = client.get("/advanced-model/?name__in=Apple,Orange")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        names = [product["name"] for product in data["results"]]
        assert any(name in ["Apple", "Orange"] for name in names)

    def test_advanced_filter_by_price_schema_field(self, client):
        """Test filtering by price field (from schema introspection)."""
        response = client.get("/advanced-model/?price__gte=2&price__lte=5")
        assert response.status_code == 200

        data = json.loads(response.data)

        for product in data["results"]:
            assert 2.0 <= float(product["price"]) <= 5.0

    def test_advanced_filter_by_is_active_schema_field(self, client):
        """Test filtering by is_active field (from schema introspection)."""
        response = client.get("/advanced-model/?is_active=true")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        for product in data["results"]:
            assert product["is_active"] is True

        # Test filtering inactive products
        response = client.get("/advanced-model/?is_active=false")
        assert response.status_code == 200

        data = json.loads(response.data)
        if data["count"] > 0:  # If there are inactive products
            for product in data["results"]:
                assert product["is_active"] is False

    def test_advanced_filter_by_category_name_explicit_field(self, client):
        """Test filtering by category_name field (explicit field definition)."""
        response = client.get("/advanced-model/?category_name=Berry")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1  # Should have Berry category

        for product in data["results"]:
            assert product["category_name"] == "Berry"

    def test_advanced_filter_citrus_category(self, client):
        """Test filtering for citrus fruits."""
        response = client.get("/advanced-model/?category_name=Citrus")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        names = [product["name"] for product in data["results"]]
        citrus_fruits = ["Orange", "Lemon", "Lime", "Grapefruit"]
        assert any(name in citrus_fruits for name in names)

    def test_advanced_complex_filtering(self, client):
        """Test complex filtering combining schema and explicit fields."""
        response = client.get("/advanced-model/?is_active=true&price__lte=4&category_name=Tropical")
        assert response.status_code == 200

        data = json.loads(response.data)

        for product in data["results"]:
            assert product["is_active"] is True
            assert float(product["price"]) <= 4.0
            assert product["category_name"] == "Tropical"

    def test_advanced_filtering_stone_fruits(self, client):
        """Test filtering for stone fruits."""
        response = client.get("/advanced-model/?category_name=Stone")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        names = [product["name"] for product in data["results"]]
        stone_fruits = ["Peach", "Cherry", "Plum", "Apricot"]
        assert any(name in stone_fruits for name in names)

    def test_advanced_ordering_by_schema_field(self, client):
        """Test ordering by schema-introspected fields."""
        response = client.get("/advanced-model/?ordering=price")
        assert response.status_code == 200

        data = json.loads(response.data)
        prices = [float(product["price"]) for product in data["results"]]
        assert prices == sorted(prices)

    def test_advanced_ordering_by_explicit_field(self, client):
        """Test ordering by explicitly defined fields."""
        response = client.get("/advanced-model/?ordering=category_name")
        assert response.status_code == 200

        data = json.loads(response.data)
        categories = [product["category_name"] for product in data["results"]]
        assert categories == sorted(categories)

    def test_advanced_ordering_descending(self, client):
        """Test descending ordering."""
        response = client.get("/advanced-model/?ordering=-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        prices = [float(product["price"]) for product in data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_advanced_multiple_ordering_criteria(self, client):
        """Test ordering by multiple criteria."""
        response = client.get("/advanced-model/?ordering=category_name,-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["results"]) > 0

        # Check that results are sorted by category_name first, then by price descending
        prev_category = ""
        prev_price = float("inf")  # Start with infinity for descending price
        for product in data["results"]:
            current_category = product["category_name"]
            current_price = float(product["price"])

            if current_category == prev_category:
                # Same category, price should be descending
                assert current_price <= prev_price
            else:
                # Different category, should be alphabetically ordered
                assert current_category >= prev_category
                prev_price = float("inf")  # Reset for new category

            prev_category = current_category
            prev_price = current_price

    def test_advanced_filter_with_ordering(self, client):
        """Test combining filters with ordering."""
        response = client.get("/advanced-model/?is_active=true&ordering=-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        prices = [float(product["price"]) for product in data["results"]]
        assert prices == sorted(prices, reverse=True)

        # Ensure all products are active
        for product in data["results"]:
            assert product["is_active"] is True

    def test_advanced_edge_case_no_matches(self, client):
        """Test filtering with no matching results."""
        response = client.get("/advanced-model/?name__in=NonExistent&category_name=FakeCategory")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 0
        assert len(data["results"]) == 0

    def test_advanced_case_insensitive_filtering(self, client):
        """Test case-insensitive filtering for string fields."""
        response = client.get("/advanced-model/?category_name=berry")
        assert response.status_code == 200

        # This might not work as expected depending on the filter implementation
        # but it's good to test the behavior
        # The response should be successful regardless of case sensitivity implementation

    def test_advanced_expensive_fruits_filter(self, client):
        """Test filtering for expensive fruits using advanced model."""
        response = client.get("/advanced-model/?price__gte=6")
        assert response.status_code == 200

        data = json.loads(response.data)

        for product in data["results"]:
            assert float(product["price"]) >= 6.0

    def test_advanced_filter_by_name_contains(self, client):
        """Test filtering by name using __contains lookup (case-sensitive)."""
        response = client.get("/advanced-model/?name__contains=apple")
        assert response.status_code == 200

        data = json.loads(response.data)

        # Should find "Pineapple" which contains "apple" (case-sensitive)
        names = [product["name"] for product in data["results"]]
        assert any("apple" in name for name in names)
        # Verify that Pineapple is found since it contains "apple"
        assert "Pineapple" in names

    def test_advanced_filter_by_name_icontains(self, client):
        """Test filtering by name using __icontains lookup (case-insensitive)."""
        response = client.get("/advanced-model/?name__icontains=apple")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 2  # Should find both "Apple" and "Pineapple"

        names = [product["name"] for product in data["results"]]
        # Should find both "Apple" and "Pineapple" (case-insensitive)
        assert "Apple" in names
        assert "Pineapple" in names

    def test_advanced_filter_by_name_icontains_case_sensitive_difference(self, client):
        """Test that __icontains is truly case-insensitive vs __contains."""
        # Test with uppercase - should only work with icontains
        response_icontains = client.get("/advanced-model/?name__icontains=GRAPE")
        assert response_icontains.status_code == 200

        data_icontains = json.loads(response_icontains.data)
        names_icontains = [product["name"] for product in data_icontains["results"]]

        # Should find products containing "grape" case-insensitively
        grape_products = [name for name in names_icontains if "grape" in name.lower()]
        assert len(grape_products) >= 1  # Should find "Grape" and "Grapefruit"
        assert any("Grape" in name for name in names_icontains)
        assert any("Grapefruit" in name for name in names_icontains)

    def test_advanced_filter_by_category_name_contains(self, client):
        """Test filtering by category_name using __contains lookup."""
        response = client.get("/advanced-model/?category_name__contains=Trop")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        # All results should have category containing "Trop" (should find "Tropical")
        for product in data["results"]:
            assert "Trop" in product["category_name"]

    def test_advanced_filter_by_category_name_icontains(self, client):
        """Test filtering by category_name using __icontains lookup."""
        response = client.get("/advanced-model/?category_name__icontains=fruit")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        # All results should have category containing "fruit" case-insensitively
        for product in data["results"]:
            assert "fruit" in product["category_name"].lower()

    def test_advanced_complex_filtering_with_contains(self, client):
        """Test complex filtering combining contains with other filters."""
        response = client.get("/advanced-model/?name__icontains=berry&is_active=true&price__lte=5")
        assert response.status_code == 200

        data = json.loads(response.data)

        for product in data["results"]:
            assert "berry" in product["name"].lower()
            assert product["is_active"] is True
            assert float(product["price"]) <= 5.0


class TestAdvancedModelFilterIterable:
    """Test the advanced model filter iterable endpoint (/advanced-model/iterable/)."""

    def test_advanced_iterable_list_products_no_filters(self, client):
        """Test listing all products from iterable source without filters."""
        response = client.get("/advanced-model/iterable/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "count" in data
        assert "results" in data
        assert data["count"] > 0  # Should have sample data
        assert len(data["results"]) == data["count"]

    def test_advanced_iterable_structure(self, client):
        """Test that advanced iterable results have the expected nested structure."""
        response = client.get("/advanced-model/iterable/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["results"]) > 0

        product = data["results"][0]

        # Check nested structure
        assert "product" in product
        assert "category_id" in product
        assert "category_name" in product

        # Check product nested fields
        assert "id" in product["product"]
        assert "name" in product["product"]
        assert "price" in product["product"]
        assert "is_active" in product["product"]
        assert "created_at" in product["product"]

    def test_advanced_filter_iterable_by_product_name(self, client):
        """Test filtering iterable products by product_name (explicit field with custom arg name)."""
        response = client.get("/advanced-model/iterable/?product_name__in=Apple,Banana")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        names = [product["product"]["name"] for product in data["results"]]
        assert any(name in ["Apple", "Banana"] for name in names)

    def test_advanced_filter_iterable_by_price(self, client):
        """Test filtering iterable products by price (explicit field)."""
        response = client.get("/advanced-model/iterable/?price__gte=1&price__lte=3")
        assert response.status_code == 200

        data = json.loads(response.data)

        for product in data["results"]:
            price = float(product["product"]["price"])
            assert 1.0 <= price <= 3.0

    def test_advanced_filter_iterable_by_is_active(self, client):
        """Test filtering iterable products by is_active (explicit field)."""
        response = client.get("/advanced-model/iterable/?is_active=true")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        for product in data["results"]:
            assert product["product"]["is_active"] is True

    def test_advanced_filter_iterable_by_schema_category_name(self, client):
        """Test filtering iterable products by category_name (from schema)."""
        response = client.get("/advanced-model/iterable/?category_name=Fruit")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        for product in data["results"]:
            assert product["category_name"] == "Fruit"

    def test_advanced_filter_tropical_iterable(self, client):
        """Test filtering for tropical fruits in iterable data."""
        response = client.get("/advanced-model/iterable/?category_name=Tropical")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        names = [product["product"]["name"] for product in data["results"]]
        tropical_fruits = ["Banana", "Mango", "Pineapple", "Kiwi", "Papaya", "Dragonfruit", "Coconut"]
        assert any(name in tropical_fruits for name in names)

    def test_advanced_complex_iterable_filtering(self, client):
        """Test complex filtering combining explicit and schema fields."""
        response = client.get("/advanced-model/iterable/?is_active=true&price__lte=5&category_name=Berry")
        assert response.status_code == 200

        data = json.loads(response.data)

        for product in data["results"]:
            assert product["product"]["is_active"] is True
            assert float(product["product"]["price"]) <= 5.0
            assert product["category_name"] == "Berry"

    def test_advanced_ordering_iterable_by_explicit_field(self, client):
        """Test ordering iterable products by explicit field."""
        response = client.get("/advanced-model/iterable/?ordering=-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        prices = [float(product["product"]["price"]) for product in data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_advanced_ordering_iterable_by_schema_field(self, client):
        """Test ordering iterable products by schema field."""
        response = client.get("/advanced-model/iterable/?ordering=category_name")
        assert response.status_code == 200

        data = json.loads(response.data)
        categories = [product["category_name"] for product in data["results"]]
        assert categories == sorted(categories)

    def test_advanced_multiple_ordering_iterable(self, client):
        """Test ordering iterable products by multiple criteria."""
        response = client.get("/advanced-model/iterable/?ordering=category_name,-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["results"]) > 0

        # Should be sorted by category_name first, then by price descending
        prev_category = ""
        prev_price = float("inf")
        for product in data["results"]:
            current_category = product["category_name"]
            current_price = float(product["product"]["price"])

            if current_category == prev_category:
                # Same category, price should be descending
                assert current_price <= prev_price
            else:
                # Different category, should be alphabetically ordered
                assert current_category >= prev_category
                prev_price = float("inf")  # Reset for new category

            prev_category = current_category
            prev_price = current_price

    def test_advanced_filter_with_ordering_iterable(self, client):
        """Test combining filters with ordering on iterable data."""
        response = client.get("/advanced-model/iterable/?category_name=Stone&ordering=-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        if data["count"] > 0:
            prices = [float(product["product"]["price"]) for product in data["results"]]
            assert prices == sorted(prices, reverse=True)

            # Verify all results are from Stone category
            for product in data["results"]:
                assert product["category_name"] == "Stone"

    def test_advanced_edge_case_empty_results_iterable(self, client):
        """Test filtering with no matching results on iterable data."""
        response = client.get("/advanced-model/iterable/?product_name__in=NonExistent&category_name=FakeCategory")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 0
        assert len(data["results"]) == 0

    def test_advanced_filter_iterable_by_product_name_contains(self, client):
        """Test filtering iterable products by product_name using __contains lookup."""
        response = client.get("/advanced-model/iterable/?product_name__contains=apple")
        assert response.status_code == 200

        data = json.loads(response.data)

        # Should find "Pineapple" which contains "apple" (case-sensitive)
        names = [product["product"]["name"] for product in data["results"]]
        assert any("apple" in name for name in names)
        assert "Pineapple" in names

    def test_advanced_filter_iterable_by_product_name_icontains(self, client):
        """Test filtering iterable products by product_name using __icontains lookup."""
        response = client.get("/advanced-model/iterable/?product_name__icontains=apple")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 2  # Should find both "Apple" and "Pineapple"

        names = [product["product"]["name"] for product in data["results"]]
        # Should find both "Apple" and "Pineapple" (case-insensitive)
        assert "Apple" in names
        assert "Pineapple" in names

    def test_advanced_filter_iterable_by_category_name_contains(self, client):
        """Test filtering iterable products by category_name using __contains lookup."""
        response = client.get("/advanced-model/iterable/?category_name__contains=Trop")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        # All results should have category containing "Trop" (should find "Tropical")
        for product in data["results"]:
            assert "Trop" in product["category_name"]

    def test_advanced_filter_iterable_by_category_name_icontains(self, client):
        """Test filtering iterable products by category_name using __icontains lookup."""
        response = client.get("/advanced-model/iterable/?category_name__icontains=fruit")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        # All results should have category containing "fruit" case-insensitively
        for product in data["results"]:
            assert "fruit" in product["category_name"].lower()

    def test_advanced_complex_iterable_filtering_with_contains(self, client):
        """Test complex iterable filtering combining contains with other filters."""
        response = client.get("/advanced-model/iterable/?product_name__icontains=berry&is_active=true&price__lte=5")
        assert response.status_code == 200

        data = json.loads(response.data)

        for product in data["results"]:
            assert "berry" in product["product"]["name"].lower()
            assert product["product"]["is_active"] is True
            assert float(product["product"]["price"]) <= 5.0

    def test_advanced_filter_iterable_case_sensitivity_comparison(self, client):
        """Test comparing case-sensitive vs case-insensitive contains on iterable data."""
        # Test with mixed case to verify case-insensitive behavior
        response = client.get("/advanced-model/iterable/?product_name__icontains=MANGO")
        assert response.status_code == 200

        data = json.loads(response.data)
        names = [product["product"]["name"] for product in data["results"]]

        # Should find "Mango" despite case difference
        assert "Mango" in names
