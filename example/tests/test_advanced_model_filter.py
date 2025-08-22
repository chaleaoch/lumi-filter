"""Tests for advanced_model_filter API endpoints."""


class TestAdvancedModelFilterBasic:
    """Test cases for /advanced-model/ endpoint using advanced model filter capabilities."""

    def test_def test_list_products_advanced_without_filters(self, client):(self, client):
        """Test listing all products using advanced model filter."""
        response = client.get("/advanced-model/")
        assert response.status_code == 200

        data = response.get_json()
        assert "count" in data
        assert "results" in data
        assert data["count"] == 6
        assert len(data["results"]) == 6

        # Verify structure includes both explicit and schema-based fields
        first_product = data["results"][0]
        expected_fields = {"id", "name", "price", "is_active", "created_at", "category_id", "category_name"}
        assert set(first_product.keys()) == expected_fields

    def test_def test_advanced_filter_by_schema_field_name(self, client):(self, client):
        """Test filtering by schema-based field (name)."""
        response = client.get("/advanced-model/?name__in=iPhone 15,Jeans")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2

        product_names = [p["name"] for p in data["results"]]
        assert "iPhone 15" in product_names
        assert "Jeans" in product_names

    def test_def test_advanced_filter_by_schema_field_price(self, client):(self, client):
        """Test filtering by schema-based field (price)."""
        response = client.get("/advanced-model/?price__gte=1000")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2  # iPhone 15 and MacBook Pro

        for product in data["results"]:
            assert float(product["price"]) >= 1000

    def test_def test_advanced_filter_by_schema_field_is_active(self, client):(self, client):
        """Test filtering by schema-based field (is_active)."""
        response = client.get("/advanced-model/?is_active=false")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 1
        assert data["results"][0]["name"] == "Apple Watch"
        assert data["results"][0]["is_active"] is False

    def test_def test_advanced_filter_by_explicit_field_category_id(self, client):(self, client):
        """Test filtering by explicit field definition (category_id)."""
        electronics_id = sample_data["categories"][0].id
        response = client.get(f"/advanced-model/?category_id={electronics_id}")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 3  # iPhone, MacBook, Apple Watch

        for product in data["results"]:
            assert product["category_id"] == electronics_id
            assert product["category_name"] == "Electronics"

    def test_def test_advanced_filter_by_explicit_field_category_name(self, client):(self, client):
        """Test filtering by explicit field definition (category_name)."""
        response = client.get("/advanced-model/?category_name=Clothing")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2  # T-Shirt and Jeans

        for product in data["results"]:
            assert product["category_name"] == "Clothing"

    def test_def test_advanced_mixed_field_filtering(self, client):(self, client):
        """Test filtering using both schema-based and explicit fields."""
        response = client.get(
            "/advanced-model/?name__in=iPhone 15,MacBook Pro&category_name=Electronics&is_active=true"
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2

        for product in data["results"]:
            assert product["name"] in ["iPhone 15", "MacBook Pro"]
            assert product["category_name"] == "Electronics"
            assert product["is_active"] is True

    def test_def test_advanced_price_range_filtering(self, client):(self, client):
        """Test advanced price range filtering."""
        response = client.get("/advanced-model/?price__gte=50&price__lte=500")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 3  # Apple Watch, Jeans, Python Book

        for product in data["results"]:
            price = float(product["price"])
            assert 50 <= price <= 500

    def test_def test_advanced_ordering_by_schema_field(self, client):(self, client):
        """Test ordering by schema-based fields."""
        response = client.get("/advanced-model/?ordering=price")
        assert response.status_code == 200

        data = response.get_json()
        prices = [float(p["price"]) for p in data["results"]]
        assert prices == sorted(prices)

    def test_def test_advanced_ordering_by_explicit_field(self, client):(self, client):
        """Test ordering by explicit field definitions."""
        response = client.get("/advanced-model/?ordering=category_name")
        assert response.status_code == 200

        data = response.get_json()
        category_names = [p["category_name"] for p in data["results"]]
        assert category_names == sorted(category_names)

    def test_def test_advanced_descending_ordering(self, client):(self, client):
        """Test descending ordering with advanced model filter."""
        response = client.get("/advanced-model/?ordering=-price")
        assert response.status_code == 200

        data = response.get_json()
        prices = [float(p["price"]) for p in data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_def test_advanced_multiple_ordering_criteria(self, client):(self, client):
        """Test multiple ordering criteria with advanced model filter."""
        response = client.get("/advanced-model/?ordering=category_name,-price")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 6

        # Verify ordering: first by category name (ascending), then by price (descending)
        prev_category = ""
        prev_price_in_category = float("inf")

        for product in data["results"]:
            current_category = product["category_name"]
            current_price = float(product["price"])

            if current_category == prev_category:
                assert current_price <= prev_price_in_category
            else:
                assert current_category >= prev_category
                prev_price_in_category = float("inf")

            prev_category = current_category
            prev_price_in_category = current_price

    def test_def test_advanced_complex_filtering_with_ordering(self, client):(self, client):
        """Test complex filtering combined with ordering."""
        response = client.get("/advanced-model/?is_active=true&price__gte=50&ordering=-price")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 4  # All active products with price >= 50

        # Verify all conditions
        for product in data["results"]:
            assert product["is_active"] is True
            assert float(product["price"]) >= 50

        # Verify ordering
        prices = [float(p["price"]) for p in data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_def test_advanced_filter_edge_cases(self, client):(self, client):
        """Test edge cases with advanced model filter."""
        # Test non-existent category
        response = client.get("/advanced-model/?category_name=NonExistent")
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 0
        assert data["results"] == []

        # Test invalid price range
        response = client.get("/advanced-model/?price__gte=10000")
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 0


class TestAdvancedModelFilterIterable:
    """Test cases for /advanced-model/iterable/ endpoint using advanced model with iterable data."""

    def test_def test_list_products_advanced_iterable_without_filters(self, client):(self, client):
        """Test listing all products from iterable data using advanced model filter."""
        response = client.get("/advanced-model/iterable/")
        assert response.status_code == 200

        data = response.get_json()
        assert "count" in data
        assert "results" in data
        assert data["count"] == 6
        assert len(data["results"]) == 6

        # Verify nested structure with both explicit and schema-based fields
        first_product = data["results"][0]
        assert "product" in first_product
        assert "category_id" in first_product
        assert "category_name" in first_product

    def test_def test_advanced_iterable_filter_by_explicit_field_id(self, client):(self, client):
        """Test filtering iterable data by explicit field (id)."""
        product_id = sample_data["products"][0].id
        response = client.get(f"/advanced-model/iterable/?id={product_id}")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 1
        assert data["results"][0]["product"]["id"] == product_id

    def test_def test_advanced_iterable_filter_by_explicit_field_product_name(self, client):(self, client):
        """Test filtering iterable data by explicit field (product_name)."""
        response = client.get("/advanced-model/iterable/?product_name__in=T-Shirt,Python Programming Book")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2

        product_names = [p["product"]["name"] for p in data["results"]]
        assert "T-Shirt" in product_names
        assert "Python Programming Book" in product_names

    def test_def test_advanced_iterable_filter_by_explicit_field_price(self, client):(self, client):
        """Test filtering iterable data by explicit field (price)."""
        response = client.get("/advanced-model/iterable/?price__gte=100&price__lte=1000")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 1  # Only Apple Watch
        assert data["results"][0]["product"]["name"] == "Apple Watch"

    def test_def test_advanced_iterable_filter_by_explicit_field_is_active(self, client):(self, client):
        """Test filtering iterable data by explicit field (is_active)."""
        response = client.get("/advanced-model/iterable/?is_active=false")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 1
        assert data["results"][0]["product"]["name"] == "Apple Watch"
        assert data["results"][0]["product"]["is_active"] is False

    def test_def test_advanced_iterable_filter_by_explicit_field_created_at(self, client):(self, client):
        """Test filtering iterable data by explicit field (created_at)."""
        response = client.get("/advanced-model/iterable/?created_at__gte=2024-03-01T00:00:00")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 1  # Only Apple Watch
        assert data["results"][0]["product"]["name"] == "Apple Watch"

    def test_def test_advanced_iterable_filter_by_schema_field(self, client):(self, client):
        """Test filtering iterable data by schema-based fields."""
        books_id = sample_data["categories"][2].id
        response = client.get(f"/advanced-model/iterable/?category_id={books_id}")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 1
        assert data["results"][0]["product"]["name"] == "Python Programming Book"
        assert data["results"][0]["category_id"] == books_id

    def test_def test_advanced_iterable_mixed_field_filtering(self, client):(self, client):
        """Test filtering iterable data using both explicit and schema-based fields."""
        response = client.get(
            "/advanced-model/iterable/?product_name__in=iPhone 15,MacBook Pro&category_name=Electronics&is_active=true"
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2

        for result in data["results"]:
            assert result["product"]["name"] in ["iPhone 15", "MacBook Pro"]
            assert result["category_name"] == "Electronics"
            assert result["product"]["is_active"] is True

    def test_def test_advanced_iterable_ordering_by_explicit_field(self, client):(self, client):
        """Test ordering iterable data by explicit fields."""
        response = client.get("/advanced-model/iterable/?ordering=-price")
        assert response.status_code == 200

        data = response.get_json()
        prices = [float(p["product"]["price"]) for p in data["results"]]
        assert prices == sorted(prices, reverse=True)

    def test_def test_advanced_iterable_ordering_by_schema_field(self, client):(self, client):
        """Test ordering iterable data by schema-based fields."""
        response = client.get("/advanced-model/iterable/?ordering=category_name")
        assert response.status_code == 200

        data = response.get_json()
        category_names = [p["category_name"] for p in data["results"]]
        assert category_names == sorted(category_names)

    def test_def test_advanced_iterable_complex_filtering_and_ordering(self, client):(self, client):
        """Test complex filtering and ordering on iterable data."""
        response = client.get("/advanced-model/iterable/?is_active=true&price__gte=50&ordering=category_name,-price")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 4  # Active products with price >= 50

        # Verify filtering conditions
        for result in data["results"]:
            assert result["product"]["is_active"] is True
            assert float(result["product"]["price"]) >= 50

        # Verify ordering (category name ascending, then price descending within category)
        prev_category = ""
        prev_price_in_category = float("inf")

        for result in data["results"]:
            current_category = result["category_name"]
            current_price = float(result["product"]["price"])

            if current_category == prev_category:
                assert current_price <= prev_price_in_category
            else:
                assert current_category >= prev_category
                prev_price_in_category = float("inf")

            prev_category = current_category
            prev_price_in_category = current_price

    def test_def test_advanced_iterable_date_range_filtering(self, client):(self, client):
        """Test date range filtering on iterable data."""
        response = client.get(
            "/advanced-model/iterable/?created_at__gte=2024-02-01T00:00:00&created_at__lte=2024-02-28T23:59:59"
        )
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 2  # MacBook Pro and Jeans

        for result in data["results"]:
            created_at = result["product"]["created_at"]
            assert "2024-02" in created_at

    def test_def test_advanced_iterable_price_and_category_filtering(self, client):(self, client):
        """Test combined price and category filtering on iterable data."""
        response = client.get("/advanced-model/iterable/?price__lte=100&category_name__in=Clothing,Books")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 3  # T-Shirt, Jeans, Python Book

        for result in data["results"]:
            assert float(result["product"]["price"]) <= 100
            assert result["category_name"] in ["Clothing", "Books"]

    def test_def test_advanced_iterable_multiple_ordering_criteria(self, client):(self, client):
        """Test multiple ordering criteria on iterable data."""
        response = client.get("/advanced-model/iterable/?ordering=product_name,id")
        assert response.status_code == 200

        data = response.get_json()
        assert data["count"] == 6

        # Verify ordering by product name first, then by id
        product_names = [p["product"]["name"] for p in data["results"]]
        assert product_names == sorted(product_names)
