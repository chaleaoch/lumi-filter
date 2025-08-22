"""Tests for model_filter API endpoints."""


class TestModelFilterBasic:
    """Test cases for /model/ endpoint using explicit field definitions."""

    def test_def test_list_products_without_filters(self, client):(self, client):
        """Test listing all products without any filters."""
        response = client.get("/model/")
        assert response.status_code == 200

        data = response.get_json()
        assert "count" in data
        assert "results" in data
        assert data["count"] == 6
        assert len(data["results"]) == 6

        # Verify structure of first product
        first_product = data["results"][0]
        expected_fields = {"id", "name", "price", "is_active", "created_at", "category_id", "category_name"}
        assert set(first_product.keys()) == expected_fields

    def test_def test_filter_by_name(self, client):(self, client):
        """Test filtering products by name."""
        response = client.get("/model/?name__in=iPhone 15,MacBook Pro")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2

        product_names = [p["name"] for p in data["results"]]
        assert "iPhone 15" in product_names
        assert "MacBook Pro" in product_names

    def test_def test_filter_by_price_range(self, client):(self, client):
        """Test filtering products by price range."""
        response = client.get("/model/?price__gte=100&price__lte=1000")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 1  # Only Apple Watch (399.99)
        assert data["results"][0]["name"] == "Apple Watch"

        # Test higher price range
        response = client.get("/model/?price__gte=1000")
        data = response.get_json()
        assert data["count"] == 2  # iPhone 15 and MacBook Pro

    def test_def test_filter_by_is_active(self, client):(self, client):
        """Test filtering products by active status."""
        response = client.get("/model/?is_active=true")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 5  # All except Apple Watch

        active_products = [p["name"] for p in data["results"]]
        assert "Apple Watch" not in active_products

        # Test inactive products
        response = client.get("/model/?is_active=false")
        data = response.get_json()
        assert data["count"] == 1
        assert data["results"][0]["name"] == "Apple Watch"

    def test_def test_filter_by_category_id(self, client):(self, client):
        """Test filtering products by category ID."""
        electronics_id = sample_data["categories"][0].id
        response = client.get(f"/model/?category_id={electronics_id}")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 3  # iPhone, MacBook, Apple Watch

        for product in data["results"]:
            assert product["category_id"] == electronics_id

    def test_def test_filter_by_category_name(self, client):(self, client):
        """Test filtering products by category name."""
        response = client.get("/model/?category_name=Electronics")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 3

        for product in data["results"]:
            assert product["category_name"] == "Electronics"

    def test_def test_complex_filtering(self, client):(self, client):
        """Test complex filtering with multiple conditions."""
        response = client.get("/model/?category_name=Electronics&is_active=true&price__gte=500")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2  # iPhone 15 and MacBook Pro

        for product in data["results"]:
            assert product["category_name"] == "Electronics"
            assert product["is_active"] is True
            assert float(product["price"]) >= 500

    def test_def test_ordering_ascending(self, client):(self, client):
        """Test ordering products in ascending order."""
        response = client.get("/model/?ordering=price")
        assert response.status_code == 200

        data = response.get_json()
        prices = [float(p["price"]) for p in data["results"]]
        assert prices == sorted(prices)

    def test_def test_ordering_descending(self, client):(self, client):
        """Test ordering products in descending order."""
        response = client.get("/model/?ordering=-price")
        assert response.status_code == 200

        data = response.get_json()
        prices = [float(p["price"]) for p in data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_def test_multiple_ordering_criteria(self, client):(self, client):
        """Test ordering by multiple fields."""
        response = client.get("/model/?ordering=category_name,price")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 6

        # Should be ordered by category name first, then by price
        prev_category = ""
        prev_price_in_category = 0

        for product in data["results"]:
            current_category = product["category_name"]
            current_price = float(product["price"])

            if current_category == prev_category:
                assert current_price >= prev_price_in_category
            else:
                prev_price_in_category = 0

            prev_category = current_category
            prev_price_in_category = current_price

    def test_def test_filter_by_creation_date(self, client):(self, client):
        """Test filtering products by creation date."""
        response = client.get("/model/?created_at__gte=2024-02-01T00:00:00")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 3  # MacBook Pro, Apple Watch, Jeans

        response = client.get("/model/?created_at__lte=2024-01-31T23:59:59")
        data = response.get_json()
        assert data["count"] == 3  # iPhone 15, T-Shirt, Python Book


class TestModelFilterIterable:
    """Test cases for /model/iterable/ endpoint using iterable data source."""

    def test_def test_list_products_iterable_without_filters(self, client):(self, client):
        """Test listing all products from iterable data without filters."""
        response = client.get("/model/iterable/")
        assert response.status_code == 200

        data = response.get_json()
        assert "count" in data
        assert "results" in data
        assert data["count"] == 6
        assert len(data["results"]) == 6

        # Verify nested structure
        first_product = data["results"][0]
        assert "product" in first_product
        assert "category_id" in first_product
        assert "category_name" in first_product

        product_data = first_product["product"]
        expected_product_fields = {"id", "name", "price", "is_active", "created_at"}
        assert set(product_data.keys()) == expected_product_fields

    def test_def test_filter_iterable_by_name(self, client):(self, client):
        """Test filtering iterable products by name."""
        response = client.get("/model/iterable/?name__in=T-Shirt,Jeans")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2

        product_names = [p["product"]["name"] for p in data["results"]]
        assert "T-Shirt" in product_names
        assert "Jeans" in product_names

    def test_def test_filter_iterable_by_price_range(self, client):(self, client):
        """Test filtering iterable products by price range."""
        response = client.get("/model/iterable/?price__gte=50&price__lte=100")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2  # Jeans (79.99) and Python Book (49.99)

        for result in data["results"]:
            price = float(result["product"]["price"])
            assert 50 <= price <= 100

    def test_def test_filter_iterable_by_category(self, client):(self, client):
        """Test filtering iterable products by category."""
        response = client.get("/model/iterable/?category_name=Clothing")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2  # T-Shirt and Jeans

        for result in data["results"]:
            assert result["category_name"] == "Clothing"

    def test_def test_filter_iterable_by_id(self, client):(self, client):
        """Test filtering iterable products by ID."""
        product_id = sample_data["products"][0].id
        response = client.get(f"/model/iterable/?id={product_id}")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 1
        assert data["results"][0]["product"]["id"] == product_id

    def test_def test_filter_iterable_by_active_status(self, client):(self, client):
        """Test filtering iterable products by active status."""
        response = client.get("/model/iterable/?is_active=false")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 1
        assert data["results"][0]["product"]["name"] == "Apple Watch"

    def test_def test_ordering_iterable_products(self, client):(self, client):
        """Test ordering iterable products."""
        response = client.get("/model/iterable/?ordering=-price")
        assert response.status_code == 200

        data = response.get_json()
        prices = [float(p["product"]["price"]) for p in data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_def test_complex_iterable_filtering(self, client):(self, client):
        """Test complex filtering on iterable data."""
        response = client.get("/model/iterable/?is_active=true&price__lte=100&ordering=price")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 3  # T-Shirt, Python Book, Jeans

        for result in data["results"]:
            assert result["product"]["is_active"] is True
            assert float(result["product"]["price"]) <= 100

        # Verify ordering
        prices = [float(p["product"]["price"]) for p in data["results"]]
        assert prices == sorted(prices)

    def test_def test_filter_iterable_by_creation_date_range(self, client):(self, client):
        """Test filtering iterable products by creation date range."""
        response = client.get(
            "/model/iterable/?created_at__gte=2024-02-01T00:00:00&created_at__lte=2024-02-28T23:59:59"
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2  # MacBook Pro and Jeans

        for result in data["results"]:
            created_at = result["product"]["created_at"]
            assert "2024-02" in created_at
