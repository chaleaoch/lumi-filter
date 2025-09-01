# lumi_filter
<!-- GitHub Actions Badge -->
![CI](https://github.com/chaleaoch/lumi_filter/workflows/CI%20Tests%20and%20Coverage/badge.svg)

<!-- Codecov Badge -->
[![codecov](https://codecov.io/gh/chaleaoch/lumi_filter/branch/main/graph/badge.svg)](https://codecov.io/gh/chaleaoch/lumi_filter)

> For specific use cases, please refer to the examples:
[Examples](https://github.com/chaleaoch/lumi_filter/tree/main/example)

lumi_filter is a powerful and flexible data filtering library designed to simplify how you filter and sort data across different data sources in your Python applications. Whether you're dealing with database queries, API responses, or in-memory data structures, lumi_filter provides a unified, intuitive interface that makes complex filtering operations effortless. Inspired by Django REST Framework's filtering system, lumi_filter has been redesigned to support multiple backends and data sources. Flask-friendly and compatible.

lumi_filter is a model-based filtering library that bridges the gap between different data sources and filtering needs. At its core, it provides a consistent API for filtering the following data sources:

- **Peewee ORM queries** - Direct database filtering through automatic SQL generation
- **Pydantic models** - Filter structured data with type validation
- **Iterable data structures** - Filter lists, dictionaries, and other Python collections

This library eliminates the need to write different filtering logic for each data source, allowing you to define filtering requirements once and apply them universally.

## Why Choose lumi_filter?

### Unified Filtering Interface

Suppose you need to implement filtering functionality throughout your application that needs to handle both database records and API responses. Without lumi_filter, you would typically need to write separate filtering logic for each data source:

#### Database Filtering (Peewee)

```python
query = Product.select().where(Product.name.contains("apple") & Product.price >= 100)
```

#### List Filtering (Python)

```python
filtered_products = [p for p in products if "apple" in p["name"] and p["price"] >= 100]
```

With lumi_filter, you define the filtering model once and use it everywhere:

```python
class FilterProduct(Model):
    name = StrField(source="name")
    price = DecimalField(source="price")
```

#### For Database Queries

```python
db_filter = FilterProduct(Product.select(), request.args)
filtered_query = db_filter.filter().result()
```

#### For Iterable Data

```python
list_filter = FilterProduct(products_list, request.args)
filtered_list = list_filter.filter().result()
```

## Rich Filtering Expressions

lumi_filter supports a comprehensive set of filtering operators that go beyond simple equality checks:

| Operator | Description | Example |
|----------|-------------|---------|
| (none) | Exact match | name=Apple |
| __in | In value list | name__in=Apple,Orange |
| __nin | Not in value list | name__nin=Apple,Orange |
| __gte | Greater than or equal | price__gte=100 |
| __lte | Less than or equal | price__lte=500 |
| __contains | Contains substring | name__contains=apple |
| __startswith | Starts with | name__startswith=A |
| __endswith | Ends with | name__endswith=e |

## Automatic Type Detection and Mapping

The library intelligently detects field types and maps them to appropriate filter fields, supporting:

- String fields with pattern matching
- Numeric fields with range comparisons
- Date/time fields with temporal filtering
- Boolean fields with truthiness filtering
- Nested fields with dot notation support

## TODO

- [ ] Support for pagination
- [ ] Field-level permission control
- [ ] Field-level custom filtering
- [ ] Support for more ORMs (e.g., SQLAlchemy)
