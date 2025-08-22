"""Tests for model_filter API endpoints.

This test suite validates the model filter endpoints using data from init_db().
The init_db() function creates 25 products across 8 categories with prices ranging from 0.55 to 7.90.
Active products: 23, Inactive products: 2 (Watermelon, Coconut)
"""

import json


class TestModelFilterAPI:
    """Test cases for model filter endpoints."""

    def test_model_filter_basic_list(self, client):
        """Test basic listing without filters."""
        response = client.get("/model/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "count" in data
        assert "results" in data
        assert data["count"] == 25
        assert len(data["results"]) == 25

        # Check structure of first item
        first_item = data["results"][0]
        expected_keys = {"id", "name", "price", "is_active", "created_at", "category_id", "category_name"}
        assert set(first_item.keys()) == expected_keys

    def test_model_filter_price_range(self, client):
        """Test price range filtering."""
        response = client.get("/model/?price__gte=1.0&price__lte=2.0")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should return products with price between 1.0 and 2.0
        # Apple: 1.50, Orange: 2.00, Carrot: 1.25
        assert data["count"] == 3

        for item in data["results"]:
            price = float(item["price"])
            assert 1.0 <= price <= 2.0

    def test_model_filter_name_in(self, client):
        """Test name in filter."""
        response = client.get("/model/?name__in=Apple,Milk")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 2

        names = [item["name"] for item in data["results"]]
        assert "Apple" in names
        assert "Milk" in names

    def test_model_filter_category_id(self, client):
        """Test filtering by category ID."""
        # First get a category ID from the data
        response = client.get("/model/")
        all_data = json.loads(response.data)
        fruit_category_id = None
        for item in all_data["results"]:
            if item["category_name"] == "Fruit":
                fruit_category_id = item["category_id"]
                break

        assert fruit_category_id is not None

        # Now filter by that category ID
        response = client.get(f"/model/?category_id={fruit_category_id}")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 3  # 3 fruits

        for item in data["results"]:
            assert item["category_id"] == fruit_category_id
            assert item["category_name"] == "Fruit"

    def test_model_filter_is_active(self, client):
        """Test filtering by active status."""
        response = client.get("/model/?is_active=false")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 2  # Watermelon and Coconut are inactive
        assert data["results"][0]["name"] == "Broccoli"
        assert data["results"][0]["is_active"] is False

    def test_model_filter_combined(self, client):
        """Test combining multiple filters."""
        response = client.get("/model/?category_name=Fruit&is_active=true&price__lte=1.5")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should return Banana (0.75) and Apple (1.50)
        assert data["count"] == 2

        for item in data["results"]:
            assert item["category_name"] == "Fruit"
            assert item["is_active"] is True
            assert float(item["price"]) <= 1.5

    def test_model_filter_ordering_asc(self, client):
        """Test ascending ordering."""
        response = client.get("/model/?ordering=price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 25

        # Check if ordered by price ascending
        prices = [float(item["price"]) for item in data["results"]]
        assert prices == sorted(prices)

    def test_model_filter_ordering_desc(self, client):
        """Test descending ordering."""
        response = client.get("/model/?ordering=-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 25

        # Check if ordered by price descending
        prices = [float(item["price"]) for item in data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_model_filter_multiple_ordering(self, client):
        """Test multiple field ordering."""
        response = client.get("/model/?ordering=category_name,price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 25

        # Check if ordered by category_name first, then price
        prev_category = ""
        prev_price_in_category = -1

        for item in data["results"]:
            current_category = item["category_name"]
            current_price = float(item["price"])

            if current_category != prev_category:
                # New category, reset price tracking
                prev_price_in_category = current_price
                prev_category = current_category
            else:
                # Same category, price should be >= previous price
                assert current_price >= prev_price_in_category
                prev_price_in_category = current_price


class TestModelFilterIterableAPI:
    """Test cases for model filter iterable endpoints."""

    def test_model_iterable_basic_list(self, client):
        """Test basic listing for iterable endpoint."""
        response = client.get("/model/iterable/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "count" in data
        assert "results" in data
        assert data["count"] == 25
        assert len(data["results"]) == 25

    def test_model_iterable_price_filter(self, client):
        """Test price filtering in iterable endpoint."""
        response = client.get("/model/iterable/?price__gte=2.5")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should return Broccoli (2.50) and Milk (3.00)
        assert data["count"] == 2

        for item in data["results"]:
            assert float(item["product"]["price"]) >= 2.5

    def test_model_iterable_name_filter(self, client):
        """Test name filtering in iterable endpoint."""
        response = client.get("/model/iterable/?name__in=Apple,Carrot")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 2

        names = [item["product"]["name"] for item in data["results"]]
        assert "Apple" in names
        assert "Carrot" in names

    def test_model_iterable_category_filter(self, client):
        """Test category filtering in iterable endpoint."""
        response = client.get("/model/iterable/?category_name=Dairy")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 1
        assert data["results"][0]["product"]["name"] == "Milk"
        assert data["results"][0]["category_name"] == "Dairy"

    def test_model_iterable_ordering(self, client):
        """Test ordering in iterable endpoint."""
        response = client.get("/model/iterable/?ordering=-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 25

        # Check if ordered by price descending
        prices = [float(item["product"]["price"]) for item in data["results"]]
        assert prices == sorted(prices, reverse=True)
