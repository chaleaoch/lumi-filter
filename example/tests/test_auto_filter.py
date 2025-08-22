"""Tests for auto_filter API endpoints."""


class TestAutoFilterBasic:
    """Test cases for /auto/ endpoint using automatic field introspection."""

    def test_list_products_auto_without_filters(self, client, sample_data):
        """Test listing all products using automatic field detection."""
        response = client.get("/auto/")
        assert response.status_code == 200

        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 6

        # Verify structure of first product
        first_product = data[0]
        expected_fields = {"id", "name", "price", "is_active", "created_at", "category_id", "category_name"}
        assert set(first_product.keys()) == expected_fields

    def test_auto_filter_by_name(self, client, sample_data):
        """Test auto-filtering products by name."""
        response = client.get("/auto/?name__in=iPhone 15,T-Shirt")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) == 2

        product_names = [p["name"] for p in data]
        assert "iPhone 15" in product_names
        assert "T-Shirt" in product_names

    def test_auto_filter_by_price_range(self, client, sample_data):
        """Test auto-filtering products by price range."""
        response = client.get("/auto/?price__gte=100&price__lte=1000")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) == 1  # Only Apple Watch
        assert data[0]["name"] == "Apple Watch"

        # Test minimum price filter
        response = client.get("/auto/?price__gte=2000")
        data = response.get_json()
        assert len(data) == 1  # Only MacBook Pro
        assert data[0]["name"] == "MacBook Pro"

    def test_auto_filter_by_is_active(self, client, sample_data):
        """Test auto-filtering products by active status."""
        response = client.get("/auto/?is_active=true")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) == 5  # All except Apple Watch

        active_product_names = [p["name"] for p in data]
        assert "Apple Watch" not in active_product_names

        # Test inactive products
        response = client.get("/auto/?is_active=false")
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Apple Watch"

    def test_auto_filter_by_category_id(self, client, sample_data):
        """Test auto-filtering products by category ID."""
        clothing_id = sample_data["categories"][1].id  # Clothing category
        response = client.get(f"/auto/?category_id={clothing_id}")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) == 2  # T-Shirt and Jeans

        for product in data:
            assert product["category_id"] == clothing_id

    def test_auto_filter_by_category_name(self, client, sample_data):
        """Test auto-filtering products by category name."""
        response = client.get("/auto/?category_name=Books")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Python Programming Book"
        assert data[0]["category_name"] == "Books"

    def test_auto_complex_filtering(self, client, sample_data):
        """Test complex auto-filtering with multiple conditions."""
        response = client.get("/auto/?category_name=Electronics&is_active=true&price__gte=800")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) == 2  # iPhone 15 and MacBook Pro

        for product in data:
            assert product["category_name"] == "Electronics"
            assert product["is_active"] is True
            assert float(product["price"]) >= 800

    def test_auto_ordering_ascending(self, client, sample_data):
        """Test auto-ordering products in ascending order."""
        response = client.get("/auto/?ordering=price")
        assert response.status_code == 200

        data = response.get_json()
        prices = [float(p["price"]) for p in data]
        assert prices == sorted(prices)

    def test_auto_ordering_descending(self, client, sample_data):
        """Test auto-ordering products in descending order."""
        response = client.get("/auto/?ordering=-price")
        assert response.status_code == 200

        data = response.get_json()
        prices = [float(p["price"]) for p in data]
        assert prices == sorted(prices, reverse=True)

    def test_auto_multiple_ordering_criteria(self, client, sample_data):
        """Test auto-ordering by multiple fields."""
        response = client.get("/auto/?ordering=category_name,-price")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) == 6

        # Verify that categories are ordered alphabetically (Books first)
        assert data[0]["category_name"] == "Books"

        # Group Electronics products and verify price ordering within category
        electronics_products = [p for p in data if p["category_name"] == "Electronics"]
        if len(electronics_products) > 1:
            electronics_prices = [float(p["price"]) for p in electronics_products]
            assert electronics_prices == sorted(electronics_prices, reverse=True)

    def test_auto_filter_by_id(self, client, sample_data):
        """Test auto-filtering by product ID."""
        product_id = sample_data["products"][2].id  # Apple Watch
        response = client.get(f"/auto/?id={product_id}")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) == 1
        assert data[0]["id"] == product_id
        assert data[0]["name"] == "Apple Watch"

    def test_auto_filter_by_creation_date(self, client, sample_data):
        """Test auto-filtering products by creation date."""
        response = client.get("/auto/?created_at__gte=2024-03-01T00:00:00")
        assert response.status_code == 200

        data = response.get_json()
        assert len(data) == 1  # Only Apple Watch
        assert data[0]["name"] == "Apple Watch"

        # Test date range
        response = client.get("/auto/?created_at__gte=2024-01-01T00:00:00&created_at__lte=2024-01-31T23:59:59")
        data = response.get_json()
        assert len(data) == 3  # iPhone 15, T-Shirt, Python Book


class TestAutoFilterIterable:
    """Test cases for /auto/iterable/ endpoint using automatic field introspection on iterable data."""

    def test_list_products_iterable_auto_without_filters(self, client, sample_data):
        """Test listing all products from iterable data using auto-detection."""
        response = client.get("/auto/iterable/")
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

    def test_auto_filter_iterable_by_nested_name(self, client, sample_data):
        """Test auto-filtering iterable products by nested product name."""
        response = client.get("/auto/iterable/?product.name__in=MacBook Pro,Python Programming Book")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2

        product_names = [p["product"]["name"] for p in data["results"]]
        assert "MacBook Pro" in product_names
        assert "Python Programming Book" in product_names

    def test_auto_filter_iterable_by_nested_price(self, client, sample_data):
        """Test auto-filtering iterable products by nested price."""
        response = client.get("/auto/iterable/?product.price__gte=100&product.price__lte=500")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 1  # Only Apple Watch
        assert data["results"][0]["product"]["name"] == "Apple Watch"

    def test_auto_filter_iterable_by_nested_active_status(self, client, sample_data):
        """Test auto-filtering iterable products by nested active status."""
        response = client.get("/auto/iterable/?product.is_active=false")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 1
        assert data["results"][0]["product"]["name"] == "Apple Watch"

    def test_auto_filter_iterable_by_top_level_category(self, client, sample_data):
        """Test auto-filtering iterable products by top-level category fields."""
        response = client.get("/auto/iterable/?category_name=Clothing")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2

        for result in data["results"]:
            assert result["category_name"] == "Clothing"

    def test_auto_filter_iterable_by_category_id(self, client, sample_data):
        """Test auto-filtering iterable products by category ID."""
        books_id = sample_data["categories"][2].id  # Books category
        response = client.get(f"/auto/iterable/?category_id={books_id}")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 1
        assert data["results"][0]["product"]["name"] == "Python Programming Book"

    def test_auto_filter_iterable_by_nested_id(self, client, sample_data):
        """Test auto-filtering iterable products by nested product ID."""
        product_id = sample_data["products"][1].id  # MacBook Pro
        response = client.get(f"/auto/iterable/?product.id={product_id}")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 1
        assert data["results"][0]["product"]["name"] == "MacBook Pro"

    def test_auto_ordering_iterable_by_nested_field(self, client, sample_data):
        """Test auto-ordering iterable products by nested fields."""
        response = client.get("/auto/iterable/?ordering=-product.price")
        assert response.status_code == 200

        data = response.get_json()
        prices = [float(p["product"]["price"]) for p in data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_auto_ordering_iterable_by_top_level_field(self, client, sample_data):
        """Test auto-ordering iterable products by top-level fields."""
        response = client.get("/auto/iterable/?ordering=category_name")
        assert response.status_code == 200

        data = response.get_json()
        category_names = [p["category_name"] for p in data["results"]]
        assert category_names == sorted(category_names)

    def test_auto_complex_iterable_filtering(self, client, sample_data):
        """Test complex auto-filtering on iterable data with nested and top-level fields."""
        response = client.get(
            "/auto/iterable/?product.is_active=true&category_name=Electronics&product.price__gte=1000"
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2  # iPhone 15 and MacBook Pro

        for result in data["results"]:
            assert result["product"]["is_active"] is True
            assert result["category_name"] == "Electronics"
            assert float(result["product"]["price"]) >= 1000

    def test_auto_filter_iterable_by_creation_date(self, client, sample_data):
        """Test auto-filtering iterable products by creation date."""
        response = client.get("/auto/iterable/?product.created_at__gte=2024-02-01T00:00:00")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 3  # MacBook Pro, Apple Watch, Jeans

        for result in data["results"]:
            created_at = result["product"]["created_at"]
            assert "2024-02" in created_at or "2024-03" in created_at

    def test_auto_multiple_ordering_iterable(self, client, sample_data):
        """Test multiple ordering criteria on iterable data."""
        response = client.get("/auto/iterable/?ordering=category_name,-product.price")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 6

        # Verify that results are first ordered by category name, then by price (descending)
        prev_category = ""
        prev_price_in_category = float("inf")

        for result in data["results"]:
            current_category = result["category_name"]
            current_price = float(result["product"]["price"])

            if current_category == prev_category:
                # Within same category, price should be descending
                assert current_price <= prev_price_in_category
            else:
                # New category should be >= previous category (alphabetical order)
                assert current_category >= prev_category
                prev_price_in_category = float("inf")

            prev_category = current_category
            prev_price_in_category = current_price
