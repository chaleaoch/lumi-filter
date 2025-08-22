"""Tests for advanced_model_filter API endpoints.

This test suite validates the advanced model filter endpoints using data from init_db().
The init_db() function creates 25 products across 8 categories:
- Berry: Grape(3.10), Strawberry(4.50), Blueberry(5.10), Avocado(3.30), Pomegranate(5.60) - all active
- Citrus: Orange(2.50), Lemon(0.60), Lime(0.55), Grapefruit(1.60) - all active
- Fruit: Apple(1.20), Pear(1.85), Fig(3.95), Date(6.10) - all active
- Melon: Watermelon(6.30) - inactive
- Stone: Peach(2.20), Cherry(6.80), Plum(2.05), Apricot(2.15) - all active
- Tropical: Banana(0.80), Mango(2.90), Pineapple(3.70), Kiwi(1.10), Papaya(2.40), Dragonfruit(7.90), Coconut(4.20) - Coconut is inactive, others active

Active products: 23, Inactive products: 2 (Watermelon, Coconut)
"""

import json


class TestAdvancedModelFilterAPI:
    """Test cases for advanced model filter API endpoints."""

    def test_advanced_filter_basic_list(self, client):
        """Test basic listing without filters."""
        response = client.get("/advanced-model/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "count" in data
        assert "results" in data
        assert data["count"] == 25  # Total 25 products from init_db

    def test_advanced_filter_name_in(self, client):
        """Test name in filter with advanced model."""
        response = client.get("/advanced-model/?name__in=Apple,Orange,Banana")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 3

        # Check that returned products have the correct names
        product_names = [item["name"] for item in data["results"]]
        expected_names = {"Apple", "Orange", "Banana"}
        assert set(product_names) == expected_names

    def test_advanced_filter_price_range(self, client):
        """Test price range filtering."""
        response = client.get("/advanced-model/?price__gte=1.0&price__lte=2.5")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Products with price between 1.0 and 2.5:
        # Apple(1.20), Orange(2.50), Pear(1.85), Peach(2.20), Kiwi(1.10), Papaya(2.40), Plum(2.05), Apricot(2.15), Grapefruit(1.60)
        assert data["count"] == 9

        for item in data["results"]:
            price = float(item["price"])
            assert 1.0 <= price <= 2.5

    def test_advanced_filter_is_active(self, client):
        """Test filtering by active status."""
        response = client.get("/advanced-model/?is_active=true")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 23  # All except Watermelon and Coconut are active

        for item in data["results"]:
            assert item["is_active"] is True

    def test_advanced_filter_is_inactive(self, client):
        """Test filtering by inactive status."""
        response = client.get("/advanced-model/?is_active=false")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 2  # Only Watermelon and Coconut are inactive

        inactive_names = [item["name"] for item in data["results"]]
        assert set(inactive_names) == {"Watermelon", "Coconut"}

    def test_advanced_filter_category_id(self, client):
        """Test filtering by category ID."""
        # First get a category ID
        response = client.get("/advanced-model/")
        all_data = json.loads(response.data)
        berry_category_id = None
        for item in all_data["results"]:
            if item["category_name"] == "Berry":
                berry_category_id = item["category_id"]
                break

        assert berry_category_id is not None

        # Filter by category ID
        response = client.get(f"/advanced-model/?category_id={berry_category_id}")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Berry category has: Grape, Strawberry, Blueberry, Avocado, Pomegranate = 5 products
        assert data["count"] == 5

        for item in data["results"]:
            assert item["category_id"] == berry_category_id
            assert item["category_name"] == "Berry"

    def test_advanced_filter_category_name(self, client):
        """Test filtering by category name."""
        response = client.get("/advanced-model/?category_name=Citrus")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 4  # Orange, Lemon, Lime, Grapefruit

        citrus_names = [item["name"] for item in data["results"]]
        expected_citrus = {"Orange", "Lemon", "Lime", "Grapefruit"}
        assert set(citrus_names) == expected_citrus

        for item in data["results"]:
            assert item["category_name"] == "Citrus"

    def test_advanced_filter_combined(self, client):
        """Test combining multiple filters."""
        response = client.get("/advanced-model/?name__in=Apple,Orange,Banana&is_active=true&price__gte=1.0")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should return Apple (1.20) and Orange (2.50), but not Banana (0.80 < 1.0)
        assert data["count"] == 2

        names = [item["name"] for item in data["results"]]
        assert "Apple" in names
        assert "Orange" in names
        assert "Banana" not in names

    def test_advanced_filter_ordering_asc(self, client):
        """Test ascending ordering."""
        response = client.get("/advanced-model/?ordering=price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 25

        # Check if ordered by price ascending
        prices = [float(item["price"]) for item in data["results"]]
        assert prices == sorted(prices)
        # First should be cheapest (Lime: 0.55), last should be most expensive (Dragonfruit: 7.90)
        assert data["results"][0]["name"] == "Lime"
        assert data["results"][-1]["name"] == "Dragonfruit"

    def test_advanced_filter_ordering_desc(self, client):
        """Test descending ordering."""
        response = client.get("/advanced-model/?ordering=-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 25

        # Check if ordered by price descending
        prices = [float(item["price"]) for item in data["results"]]
        assert prices == sorted(prices, reverse=True)
        # First should be most expensive (Dragonfruit: 7.90), last should be cheapest (Lime: 0.55)
        assert data["results"][0]["name"] == "Dragonfruit"
        assert data["results"][-1]["name"] == "Lime"


class TestAdvancedModelFilterIterableAPI:
    """Test cases for advanced model filter iterable API endpoints."""

    def test_advanced_iterable_basic_list(self, client):
        """Test basic listing for iterable endpoint."""
        response = client.get("/advanced-model/iterable/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "count" in data
        assert "results" in data
        assert data["count"] == 25

    def test_advanced_iterable_filter_by_id(self, client):
        """Test filtering by ID."""
        response = client.get("/advanced-model/iterable/?id=1")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 1
        assert data["results"][0]["id"] == 1

    def test_advanced_iterable_filter_by_product_name(self, client):
        """Test filtering by product name."""
        response = client.get("/advanced-model/iterable/?product_name__in=Apple,Banana")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 2

        names = [item["product_name"] for item in data["results"]]
        assert set(names) == {"Apple", "Banana"}

    def test_advanced_iterable_filter_by_price(self, client):
        """Test filtering by price in nested structure."""
        response = client.get("/advanced-model/iterable/?price__lte=1.5")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Should return products with price <= 1.5
        # Apple(1.20), Banana(0.80), Lemon(0.60), Lime(0.55), Kiwi(1.10) = 5 products
        assert data["count"] == 5

        for item in data["results"]:
            assert item["price"] <= 1.5

    def test_advanced_iterable_filter_by_active_status(self, client):
        """Test filtering by active status."""
        response = client.get("/advanced-model/iterable/?is_active=false")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 2  # Watermelon and Coconut

        names = [item["product_name"] for item in data["results"]]
        assert set(names) == {"Watermelon", "Coconut"}

    def test_advanced_iterable_filter_by_category(self, client):
        """Test filtering by category name."""
        response = client.get("/advanced-model/iterable/?category_name=Tropical")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Tropical: Banana, Mango, Pineapple, Kiwi, Papaya, Dragonfruit, Coconut = 7 products
        assert data["count"] == 7

        tropical_names = [item["product_name"] for item in data["results"]]
        expected_tropical = {"Banana", "Mango", "Pineapple", "Kiwi", "Papaya", "Dragonfruit", "Coconut"}
        assert set(tropical_names) == expected_tropical

    def test_advanced_iterable_ordering(self, client):
        """Test ordering functionality."""
        response = client.get("/advanced-model/iterable/?ordering=-price")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["count"] == 25

        prices = [float(item["price"]) for item in data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_advanced_iterable_combined_filters(self, client):
        """Test combining multiple filters."""
        response = client.get("/advanced-model/iterable/?category_name=Berry&is_active=true")
        assert response.status_code == 200

        data = json.loads(response.data)
        # Berry category active products: Grape, Strawberry, Blueberry, Avocado, Pomegranate = 5 products
        assert data["count"] == 5

        for item in data["results"]:
            assert item["is_active"] is True
            # Get category name from the nested structure
            category_name = item.get("category", {}).get("name")
            assert category_name == "Berry"
