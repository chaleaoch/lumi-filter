"""Tests for basic model filter functionality.

This module tests the basic usage of custom filter models with explicit field definitions
for both database queries and iterable data structures.
"""

import json


class TestModelFilterBasic:
    """Test the basic model filter endpoint (/model/)."""

    def test_list_products_no_filters(self, client):
        """Test listing all products without any filters."""
        response = client.get("/model/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "count" in data
        assert "results" in data
        assert data["count"] > 0  # Should have sample data
        assert len(data["results"]) == data["count"]

    def test_filter_by_name_contains(self, client):
        """Test filtering products by name using __in lookup."""
        response = client.get("/model/?name__in=Apple,Orange")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1  # Should find at least Apple or Orange

        names = [product["name"] for product in data["results"]]
        # Should contain Apple and/or Orange from sample data
        assert any(name in ["Apple", "Orange"] for name in names)

    def test_filter_by_price_range(self, client):
        """Test filtering products by price range."""
        response = client.get("/model/?price__gte=3&price__lte=6")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        # Verify all results are within price range
        for product in data["results"]:
            assert 3.0 <= float(product["price"]) <= 6.0

    def test_filter_by_is_active(self, client):
        """Test filtering products by active status."""
        response = client.get("/model/?is_active=true")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        for product in data["results"]:
            assert product["is_active"] is True

        # Test filtering inactive products
        response = client.get("/model/?is_active=false")
        assert response.status_code == 200

        data = json.loads(response.data)
        if data["count"] > 0:  # If there are inactive products
            for product in data["results"]:
                assert product["is_active"] is False

    def test_filter_by_category_name(self, client):
        """Test filtering products by category name."""
        response = client.get("/model/?category_name=Fruit")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1  # Should have Fruit category products

        for product in data["results"]:
            assert product["category_name"] == "Fruit"

    def test_filter_by_category_citrus(self, client):
        """Test filtering products by Citrus category."""
        response = client.get("/model/?category_name=Citrus")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1  # Should have Citrus category products

        for product in data["results"]:
            assert product["category_name"] == "Citrus"

    def test_complex_filtering(self, client):
        """Test complex filtering with multiple conditions."""
        response = client.get("/model/?category_name=Berry&price__lte=5&is_active=true")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should find berry products under $5 that are active
        for product in data["results"]:
            assert product["category_name"] == "Berry"
            assert float(product["price"]) <= 5.0
            assert product["is_active"] is True

    def test_ordering_ascending(self, client):
        """Test ordering products in ascending order."""
        response = client.get("/model/?ordering=price")
        assert response.status_code == 200

        data = json.loads(response.data)
        prices = [float(product["price"]) for product in data["results"]]
        assert prices == sorted(prices)

    def test_ordering_descending(self, client):
        """Test ordering products in descending order."""
        response = client.get("/model/?ordering=-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        prices = [float(product["price"]) for product in data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_multiple_ordering_criteria(self, client):
        """Test ordering by multiple criteria."""
        response = client.get("/model/?ordering=category_name,price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data["results"]) > 0

        # Should be sorted by category_name first, then by price
        prev_category = ""
        prev_price = 0.0
        for product in data["results"]:
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

    def test_filter_with_ordering(self, client):
        """Test combining filters with ordering."""
        response = client.get("/model/?is_active=true&ordering=-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        prices = [float(product["price"]) for product in data["results"]]
        assert prices == sorted(prices, reverse=True)

        # Ensure all products are active
        for product in data["results"]:
            assert product["is_active"] is True

    def test_filter_tropical_fruits(self, client):
        """Test filtering for tropical fruits specifically."""
        response = client.get("/model/?category_name=Tropical")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1  # Should have tropical fruits

        names = [product["name"] for product in data["results"]]
        # Should include tropical fruits from sample data
        tropical_fruits = ["Banana", "Mango", "Pineapple", "Kiwi", "Papaya", "Dragonfruit", "Coconut"]
        assert any(name in tropical_fruits for name in names)

    def test_expensive_fruits(self, client):
        """Test filtering for expensive fruits (over $5)."""
        response = client.get("/model/?price__gte=5")
        assert response.status_code == 200

        data = json.loads(response.data)

        for product in data["results"]:
            assert float(product["price"]) >= 5.0


class TestModelFilterIterable:
    """Test the iterable model filter endpoint (/model/iterable/)."""

    def test_list_products_iterable_no_filters(self, client):
        """Test listing all products from iterable source without filters."""
        response = client.get("/model/iterable/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "count" in data
        assert "results" in data
        assert data["count"] > 0  # Should have sample data
        assert len(data["results"]) == data["count"]

    def test_iterable_structure(self, client):
        """Test that iterable results have the expected nested structure."""
        response = client.get("/model/iterable/")
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

    def test_filter_iterable_by_name(self, client):
        """Test filtering iterable products by name."""
        response = client.get("/model/iterable/?name__in=Apple,Banana")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        names = [product["product"]["name"] for product in data["results"]]
        assert any(name in ["Apple", "Banana"] for name in names)

    def test_filter_iterable_by_price(self, client):
        """Test filtering iterable products by price."""
        response = client.get("/model/iterable/?price__lte=2")
        assert response.status_code == 200

        data = json.loads(response.data)

        for product in data["results"]:
            assert float(product["product"]["price"]) <= 2.0

    def test_filter_iterable_by_category(self, client):
        """Test filtering iterable products by category."""
        response = client.get("/model/iterable/?category_name=Berry")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        for product in data["results"]:
            assert product["category_name"] == "Berry"

    def test_ordering_iterable_by_price(self, client):
        """Test ordering iterable products by price."""
        response = client.get("/model/iterable/?ordering=-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        prices = [float(product["product"]["price"]) for product in data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_filter_stone_fruits(self, client):
        """Test filtering for stone fruits specifically."""
        response = client.get("/model/iterable/?category_name=Stone")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] >= 1

        for product in data["results"]:
            assert product["category_name"] == "Stone"
