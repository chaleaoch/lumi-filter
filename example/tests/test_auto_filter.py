"""Tests for auto_filter API endpoints.

This test suite v             data = json.loads(response.data)
        # Should return inactive products (Watermelon and Coconut)
        assert len(data) == 2

        inactive_names = [item["name"] for item in data]
        assert set(inactive_names) == {"Watermelon", "Coconut"}a = json.loads(response.data)
        # Should return active products (23 total)
        assert len(data) == 23

        for item in data:
            assert item["is_active"] is Truees the auto filter endpoints using data from init_db().
The init_db() function creates 25 products across 8 categories with prices ranging from 0.55 to 7.90.
Active products: 23, Inactive products: 2 (Watermelon, Coconut)
"""

import json


class TestAutoFilterAPI:
    """Test cases for auto filter endpoints."""

    def test_auto_filter_basic_list(self, client):
        """Test basic listing without filters."""
        response = client.get("/auto/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 25  # We have 25 test products

        # Check structure of first item
        first_item = data[0]
        expected_keys = {"id", "name", "price", "is_active", "created_at", "category_id", "category_name"}
        assert set(first_item.keys()) == expected_keys

    def test_auto_filter_price_gte(self, client):
        """Test price greater than or equal filter."""
        response = client.get("/auto/?price__gte=5.0")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should return products with price >= 5.0
        # Blueberry(5.10), Pomegranate(5.60), Watermelon(6.30), Cherry(6.80), Date(6.10), Dragonfruit(7.90) = 6 products
        assert len(data) == 6

        for item in data:
            assert float(item["price"]) >= 5.0

    def test_auto_filter_price_lte(self, client):
        """Test price less than or equal filter."""
        response = client.get("/auto/?price__lte=1.5")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should return products with price <= 1.5
        # Apple(1.20), Banana(0.80), Lemon(0.60), Lime(0.55), Kiwi(1.10) = 5 products
        assert len(data) == 5

        for item in data:
            assert float(item["price"]) <= 1.5

    def test_auto_filter_is_active_true(self, client):
        """Test filtering by active status."""
        response = client.get("/auto/?is_active=true")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should return 5 active products (all except Broccoli)
        assert len(data) == 23

        for item in data:
            assert item["is_active"] is True

    def test_auto_filter_is_active_false(self, client):
        """Test filtering by inactive status."""
        response = client.get("/auto/?is_active=false")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should return 1 inactive product (Broccoli)
        assert len(data) == 1
        assert data[0]["name"] == "Broccoli"
        assert data[0]["is_active"] is False

    def test_auto_filter_name_in(self, client):
        """Test name in filter."""
        response = client.get("/auto/?name__in=Apple,Orange")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should return 2 products
        assert len(data) == 2

        names = [item["name"] for item in data]
        assert "Apple" in names
        assert "Orange" in names

    def test_auto_filter_category_name(self, client):
        """Test filtering by category name."""
        response = client.get("/auto/?category_name=Fruit")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should return 3 fruit products
        assert len(data) == 3

        for item in data:
            assert item["category_name"] == "Fruit"

    def test_auto_filter_combined_filters(self, client):
        """Test combining multiple filters."""
        response = client.get("/auto/?category_name=Fruit&is_active=true&price__gte=1.0")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should return Apple (1.50) and Orange (2.00), but not Banana (0.75)
        assert len(data) == 2

        for item in data:
            assert item["category_name"] == "Fruit"
            assert item["is_active"] is True
            assert float(item["price"]) >= 1.0

    def test_auto_filter_ordering(self, client):
        """Test ordering functionality."""
        response = client.get("/auto/?ordering=price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 25

        # Check if ordered by price ascending
        prices = [float(item["price"]) for item in data]
        assert prices == sorted(prices)

    def test_auto_filter_ordering_desc(self, client):
        """Test descending ordering functionality."""
        response = client.get("/auto/?ordering=-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 25

        # Check if ordered by price descending
        prices = [float(item["price"]) for item in data]
        assert prices == sorted(prices, reverse=True)


class TestAutoFilterIterableAPI:
    """Test cases for auto filter iterable endpoints."""

    def test_auto_iterable_basic_list(self, client):
        """Test basic listing without filters for iterable endpoint."""
        response = client.get("/auto/iterable/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "count" in data
        assert "results" in data
        assert data["count"] == 25
        assert len(data["results"]) == 25

        # Check structure of first item
        first_item = data["results"][0]
        assert "product" in first_item
        assert "category_id" in first_item
        assert "category_name" in first_item

        product = first_item["product"]
        expected_product_keys = {"id", "name", "price", "is_active", "created_at"}
        assert set(product.keys()) == expected_product_keys

    def test_auto_iterable_filter_by_price(self, client):
        """Test filtering by product price in nested structure."""
        response = client.get("/auto/iterable/?product.price__gte=2.0")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 3

        for item in data["results"]:
            assert float(item["product"]["price"]) >= 2.0

    def test_auto_iterable_filter_by_category(self, client):
        """Test filtering by category in iterable structure."""
        response = client.get("/auto/iterable/?category_name=Vegetable")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 2  # Carrot and Broccoli

        for item in data["results"]:
            assert item["category_name"] == "Vegetable"

    def test_auto_iterable_ordering(self, client):
        """Test ordering in iterable structure."""
        response = client.get("/auto/iterable/?ordering=-product.price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 25

        # Check if ordered by price descending
        prices = [float(item["product"]["price"]) for item in data["results"]]
        assert prices == sorted(prices, reverse=True)
