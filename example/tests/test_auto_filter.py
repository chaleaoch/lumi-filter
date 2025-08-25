"""Tests for automatic field introspection functionality.

This module tests automatic field detection and filtering using AutoQueryModel for both
database queries and iterable data structures.
"""

import json


class TestAutoFilter:
    """Test the automatic filter endpoint (/auto/)."""

    def test_auto_list_products_no_filters(self, client):
        """Test listing all products using auto detection without filters."""
        response = client.get("/auto/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0  # Should have sample data

    def test_auto_filter_by_name_in(self, client):
        """Test filtering products by name using __in lookup with auto detection."""
        response = client.get("/auto/?name__in=Apple,Orange")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) >= 1  # Should find Apple and/or Orange

        names = [product["name"] for product in data]
        assert any(name in ["Apple", "Orange"] for name in names)

    def test_auto_filter_by_price_range(self, client):
        """Test filtering products by price range using auto detection."""
        response = client.get("/auto/?price__gte=2&price__lte=4")
        assert response.status_code == 200

        data = json.loads(response.data)

        for product in data:
            assert 2.0 <= float(product["price"]) <= 4.0

    def test_auto_filter_by_is_active(self, client):
        """Test filtering products by active status using auto detection."""
        response = client.get("/auto/?is_active=true")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) >= 1

        for product in data:
            assert product["is_active"] is True

        # Test filtering inactive products (should include Watermelon and Coconut from sample data)
        response = client.get("/auto/?is_active=false")
        assert response.status_code == 200

        data = json.loads(response.data)
        if len(data) > 0:  # If there are inactive products
            for product in data:
                assert product["is_active"] is False

    def test_auto_filter_by_category_name(self, client):
        """Test filtering products by category name using auto detection."""
        response = client.get("/auto/?category_name=Fruit")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) >= 1  # Should have Fruit category

        for product in data:
            assert product["category_name"] == "Fruit"

    def test_auto_filter_citrus_category(self, client):
        """Test filtering for citrus fruits specifically."""
        response = client.get("/auto/?category_name=Citrus")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) >= 1  # Should have citrus fruits

        names = [product["name"] for product in data]
        citrus_fruits = ["Orange", "Lemon", "Lime", "Grapefruit"]
        assert any(name in citrus_fruits for name in names)

    def test_auto_complex_filtering(self, client):
        """Test complex filtering with multiple conditions using auto detection."""
        response = client.get("/auto/?is_active=true&price__lte=3&category_name=Berry")
        assert response.status_code == 200

        data = json.loads(response.data)

        for product in data:
            assert product["is_active"] is True
            assert float(product["price"]) <= 3.0
            assert product["category_name"] == "Berry"

    def test_auto_ordering_ascending(self, client):
        """Test ordering products in ascending order using auto detection."""
        response = client.get("/auto/?ordering=price")
        assert response.status_code == 200

        data = json.loads(response.data)
        prices = [float(product["price"]) for product in data]
        assert prices == sorted(prices)

    def test_auto_ordering_descending(self, client):
        """Test ordering products in descending order using auto detection."""
        response = client.get("/auto/?ordering=-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        prices = [float(product["price"]) for product in data]
        assert prices == sorted(prices, reverse=True)

    def test_auto_multiple_ordering(self, client):
        """Test ordering by multiple criteria using auto detection."""
        response = client.get("/auto/?ordering=category_name,price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) > 0

        # Check that results are sorted by category_name first
        prev_category = ""
        prev_price = 0.0
        for product in data:
            current_category = product["category_name"]
            current_price = float(product["price"])

            if current_category == prev_category:
                # Same category, price should be ascending
                assert current_price >= prev_price
            else:
                # Different category, should be alphabetically ordered
                assert current_category >= prev_category

            prev_category = current_category
            prev_price = current_price

    def test_auto_filter_with_ordering(self, client):
        """Test combining filters with ordering using auto detection."""
        response = client.get("/auto/?is_active=true&ordering=-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) >= 1

        # Should be ordered by price in descending order
        prices = [float(product["price"]) for product in data]
        assert prices == sorted(prices, reverse=True)

        # Ensure all products are active
        for product in data:
            assert product["is_active"] is True

    def test_auto_filter_tropical_fruits(self, client):
        """Test filtering for tropical fruits using auto detection."""
        response = client.get("/auto/?category_name=Tropical")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) >= 1

        names = [product["name"] for product in data]
        tropical_fruits = ["Banana", "Mango", "Pineapple", "Kiwi", "Papaya", "Dragonfruit", "Coconut"]
        assert any(name in tropical_fruits for name in names)

    def test_auto_filter_expensive_fruits(self, client):
        """Test filtering for expensive fruits (over $5) using auto detection."""
        response = client.get("/auto/?price__gte=5")
        assert response.status_code == 200

        data = json.loads(response.data)

        for product in data:
            assert float(product["price"]) >= 5.0


class TestAutoFilterIterable:
    """Test the automatic filter iterable endpoint (/auto/iterable/)."""

    def test_auto_iterable_list_products_no_filters(self, client):
        """Test listing all products from iterable source without filters using auto detection."""
        response = client.get("/auto/iterable/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "count" in data
        assert "results" in data
        assert data["count"] > 0  # Should have sample data
        assert len(data["results"]) == data["count"]

    def test_auto_iterable_structure(self, client):
        """Test that auto iterable results have the expected nested structure."""
        response = client.get("/auto/iterable/")
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

    def test_auto_filter_iterable_by_nested_name(self, client):
        """Test filtering iterable products by nested name using auto detection."""
        response = client.get("/auto/iterable/?product.name__in=Apple,Banana")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        names = [product["product"]["name"] for product in data["results"]]
        assert any(name in ["Apple", "Banana"] for name in names)

    def test_auto_filter_iterable_by_nested_price(self, client):
        """Test filtering iterable products by nested price using auto detection."""
        response = client.get("/auto/iterable/?product.price__gte=3&product.price__lte=5")
        assert response.status_code == 200

        data = json.loads(response.data)

        for product in data["results"]:
            price = float(product["product"]["price"])
            assert 3.0 <= price <= 5.0

    def test_auto_filter_iterable_by_nested_is_active(self, client):
        """Test filtering iterable products by nested active status using auto detection."""
        response = client.get("/auto/iterable/?product.is_active=true")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        for product in data["results"]:
            assert product["product"]["is_active"] is True

    def test_auto_filter_iterable_by_top_level_category(self, client):
        """Test filtering iterable products by top-level category fields using auto detection."""
        response = client.get("/auto/iterable/?category_name=Berry")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        for product in data["results"]:
            assert product["category_name"] == "Berry"

    def test_auto_complex_iterable_filtering(self, client):
        """Test complex filtering on iterable data using auto detection."""
        response = client.get("/auto/iterable/?product.is_active=true&category_name=Stone")
        assert response.status_code == 200

        data = json.loads(response.data)

        for product in data["results"]:
            assert product["product"]["is_active"] is True
            assert product["category_name"] == "Stone"

    def test_auto_ordering_iterable_by_nested_price(self, client):
        """Test ordering iterable products by nested price using auto detection."""
        response = client.get("/auto/iterable/?ordering=-product.price")
        assert response.status_code == 200

        data = json.loads(response.data)
        prices = [float(product["product"]["price"]) for product in data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_auto_ordering_iterable_by_nested_name(self, client):
        """Test ordering iterable products by nested name using auto detection."""
        response = client.get("/auto/iterable/?ordering=product.name")
        assert response.status_code == 200

        data = json.loads(response.data)
        names = [product["product"]["name"] for product in data["results"]]
        assert names == sorted(names)

    def test_auto_ordering_iterable_by_top_level_field(self, client):
        """Test ordering iterable products by top-level category field using auto detection."""
        response = client.get("/auto/iterable/?ordering=category_name")
        assert response.status_code == 200

        data = json.loads(response.data)
        categories = [product["category_name"] for product in data["results"]]
        assert categories == sorted(categories)
